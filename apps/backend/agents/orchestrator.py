import asyncio
import re
from typing import Any, Dict, List

from loguru import logger

from ai.errors import LLMError
from core.config import settings
from memory.session_store import redis_store
from .analyzer import analyzer_agent
from .base import validate_target_url
from .browser import browser_agent
from .cleaner import cleaner_agent
from .conversation import conversation_agent
from .exporter import export_agent
from .extractor import extractor_agent
from .memory_agent import memory_agent
from .planner import planner_agent
from .validator import validator_agent

_RESCRAPE = re.compile(r"\b(re-?run|scrape again|extract again|fetch again|refresh (the )?(data|page)|try again)\b", re.I)


class PipelineInputError(ValueError):
    """User-fixable input problem (mapped to HTTP 400 with a readable message)."""
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class PipelineOrchestrator:
    """Coordinates the 9-agent pipeline. Routing is DETERMINISTIC (not left to the LLM):

    extraction : a URL was given, a NEW file was uploaded, an explicit re-run was requested, or no dataset exists yet
    followup   : a dataset already exists and the message brings nothing new -> Conversation agent only
    idle       : nothing to work on yet
    """

    def __init__(self):
        self.planner = planner_agent
        self.analyzer = analyzer_agent
        self.browser = browser_agent
        self.extractor = extractor_agent
        self.cleaner = cleaner_agent
        self.validator = validator_agent
        self.memory = memory_agent
        self.conversation = conversation_agent
        self.exporter = export_agent

    async def _collect_uploads(self, session_id: str, consumed: set) -> Dict[str, Any]:
        ids = await redis_store.list_uploaded_context_ids(session_id)
        new_ids = [i for i in ids if i not in consumed]
        rows: List[Dict[str, Any]] = []
        texts: List[str] = []
        for fid in new_ids:
            file_rows = await redis_store.get_uploaded_rows(session_id, fid)
            if file_rows:
                rows.extend(file_rows)
            else:
                ctx = await redis_store.get_uploaded_context(session_id, fid)
                if ctx:
                    texts.append(ctx)
        return {"new_ids": new_ids, "rows": rows, "text": "\n\n---\n\n".join(texts)}

    async def execute_pipeline(self, user_request: str, target_url: str, session_id: str, owner_id: str = "") -> Dict[str, Any]:
        target_url = (target_url or "").strip()
        logger.info(f"[{session_id}] Pipeline request (url={'yes' if target_url else 'no'})")

        if target_url and not await asyncio.to_thread(validate_target_url, target_url):   # DNS lookup off the event loop
            raise PipelineInputError("INVALID_URL", "That address isn't allowed. Please use a public http(s) website URL.")

        try:
            cached = await redis_store.get_session_data(session_id)
            cached = cached if isinstance(cached, dict) else {}
            cached_rows = cached.get("cleaned_data") or []
            consumed = set(cached.get("source_upload_ids") or [])
            uploads = await self._collect_uploads(session_id, consumed)

            wants_rerun = bool(_RESCRAPE.search(user_request or "")) and bool(cached.get("target_url"))
            if wants_rerun and not target_url:
                target_url = cached["target_url"]

            if target_url or uploads["new_ids"] or not cached_rows:
                mode = "extraction" if (target_url or uploads["new_ids"]) else "idle"
            else:
                mode = "followup"
            if wants_rerun:
                mode = "extraction"

            state: Dict[str, Any] = {
                "user_request": user_request, "target_url": target_url, "owner_id": owner_id,
                "mode": mode, "data": None, "metadata": {}, "warnings": [],
            }

            if mode == "idle":
                await redis_store.clear_pipeline_progress(session_id)
                state["conversation_response"] = {
                    "response_text": "There's no data in this chat yet. Paste a public website URL or attach a file "
                                     "(CSV, Excel, PDF, Word or image) and tell me what to extract.",
                    "export_requested": "none", "result_count": None}
                state["completed_steps"] = []
                return {"status": "success", "message": "Pipeline completed.", "data": self._finalize(state)}

            completed: List[str] = []

            if mode == "extraction":
                state["uploaded_context"] = uploads["text"]
                await redis_store.set_pipeline_progress(session_id, "plan")
                state = await self.planner.run(state, session_id)
                completed.append("plan")
                state["mode"] = "extraction"
                has_url = bool(state.get("target_url"))

                if has_url:
                    await redis_store.set_pipeline_progress(session_id, "analyze")
                    state = await self.analyzer.run(state, session_id)
                    completed.append("analyze")
                    await redis_store.set_pipeline_progress(session_id, "browse")
                    state = await self.browser.run(state, session_id)
                    completed.append("browse")

                await redis_store.set_pipeline_progress(session_id, "extract")
                access_issue = state.get("url_access_issue") or state.get("analysis", {}).get("url_access_issue")
                if has_url and access_issue == "private_auth" and not (uploads["text"] or uploads["rows"]):
                    # Level 4 & 5: Page requires login / private session; skip extracting login forms
                    raw = []
                elif has_url or uploads["text"]:
                    state = await self.extractor.run(state, session_id)
                    raw = state.get("extracted_data", [])
                else:
                    raw = []
                if not has_url and uploads["rows"]:
                    raw = uploads["rows"] + raw                     # exact rows of CSV/XLSX - no LLM needed
                state["extracted_data"] = raw
                completed.append("extract")

                await redis_store.set_pipeline_progress(session_id, "clean")
                state = await self.cleaner.run(state, session_id)
                completed.append("clean")

                await redis_store.set_pipeline_progress(session_id, "validate")
                state = await self.validator.run(state, session_id)
                completed.append("validate")

                if state.get("cleaned_data"):
                    state["source_upload_ids"] = sorted(consumed | set(uploads["new_ids"]))
                    state["action"] = "save"
                    state = await self.memory.run(state, session_id)
                else:
                    state["extraction_empty"] = True
                    if cached_rows:      # keep the earlier dataset available for follow-ups
                        state["previous_rows_available"] = True
            else:
                state["detected_language"] = "auto"
                state["cleaned_data"] = cached_rows
                state["validation"] = cached.get("validation", {})
                state["expected_fields"] = cached.get("expected_fields", [])
                state["target_url"] = cached.get("target_url", "")
                completed = []

            state["completed_steps"] = completed

            if state.get("extraction_empty"):
                issue = state.get("url_access_issue") or state.get("analysis", {}).get("url_access_issue")
                if issue == "private_auth":
                    resp_text = (
                        "This URL appears to be private or requires authentication. "
                        "WEBISCRAP currently works with publicly accessible web pages. "
                        "Please provide a public URL that can be opened without logging in."
                    )
                elif issue == "access_blocked":
                    resp_text = (
                        "We couldn't access this URL because automated access was restricted or blocked by the website "
                        "(e.g. Cloudflare or bot protection). Please provide a publicly accessible URL, or try uploading "
                        "the content directly as a document (PDF, CSV, Excel, or Word)."
                    )
                elif issue in ("unreachable_timeout", "unreachable_dns", "unreachable"):
                    resp_text = (
                        "We couldn't connect to this URL. The website took too long to respond or is temporarily "
                        "unavailable. Please check that the URL is active and try again."
                    )
                else:
                    resp_text = (
                        "We couldn't access this URL. It may require authentication, block automated access, "
                        "or be temporarily unavailable. Please try a publicly accessible URL."
                    )
                state["conversation_response"] = {
                    "response_text": resp_text,
                    "export_requested": "none",
                    "result_count": None
                }
            else:
                state = await self.conversation.run(state, session_id)
                state = await self.exporter.run(state, session_id)

            await redis_store.clear_pipeline_progress(session_id)
            logger.info(f"[{session_id}] Pipeline completed (mode={state['mode']}).")
            return {"status": "success", "message": "Pipeline completed.", "data": self._finalize(state)}

        except (LLMError, PipelineInputError):
            await redis_store.clear_pipeline_progress(session_id)
            raise
        except Exception as e:
            await redis_store.clear_pipeline_progress(session_id)
            logger.exception(f"[{session_id}] Pipeline failed: {type(e).__name__}")
            return {"status": "error", "code": "PIPELINE_ERROR",
                    "message": "Something went wrong while processing your request. Please try again."}

    @staticmethod
    def _finalize(state: Dict[str, Any]) -> Dict[str, Any]:
        """Keep the response small: preview rows only (full data is served by /data and /api/export)."""
        rows = state.get("cleaned_data") or []
        state["dataset_rows"] = len(rows)
        state["dataset_cols"] = len({k for r in rows[:200] for k in r}) if rows else 0
        state["cleaned_data"] = rows[: settings.CHAT_PREVIEW_ROWS]
        state["ran_extraction"] = state.get("mode") == "extraction" and not state.get("extraction_empty")
        for heavy in ("uploaded_context", "dom_snapshots", "filtered_data", "extracted_data", "document_text"):
            state.pop(heavy, None)
        return state


orchestrator = PipelineOrchestrator()
