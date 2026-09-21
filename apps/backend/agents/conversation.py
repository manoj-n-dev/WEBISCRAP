import asyncio
import json
from typing import Any, Dict, List, Optional

from loguru import logger

from ai.errors import LLMInvalidOutputError
from ai.router import ai_router
from core.config import settings
from core.dataset_query import apply_query, dataset_stats
from core.llm_json import extract_json
from memory.session_store import redis_store
from prompts.conversation_prompt import CONVERSATION_SYSTEM_PROMPT
from .base import BaseAgent

VALID_EXPORTS = {"csv", "excel", "json", "markdown"}


def _visible_rows(dataset: List[Dict[str, Any]], budget_chars: int, max_rows: Optional[int] = None) -> List[Dict[str, Any]]:
    out, used = [], 0
    for i, row in enumerate(dataset):
        if max_rows is not None and len(out) >= max_rows:
            break
        compact = {"_id": i, **{k: (v[:120] if isinstance(v, str) else v) for k, v in row.items()}}
        size = len(json.dumps(compact, ensure_ascii=False, separators=(",", ":")))
        if used + size > budget_chars and out:
            break
        out.append(compact)
        used += size
    return out


class ConversationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ConversationAgent")

    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        user_request = input_data.get("user_request", "")
        mode = input_data.get("mode", "followup")
        language = input_data.get("detected_language") or "auto"
        dataset: List[Dict[str, Any]] = input_data.get("cleaned_data", []) or []

        history = await redis_store.get_conversation_history(session_id)
        recent = [{"role": h.get("role"), "content": str(h.get("content", ""))[:300]} for h in history[-4:]]

        budget = 20000 if settings.groq_is_paid_tier else 6000
        visible = _visible_rows(dataset, budget, max_rows=10 if mode == "extraction" else None)
        all_visible = len(visible) >= len(dataset)
        stats = await asyncio.to_thread(dataset_stats, dataset) if dataset else {}

        prompt = f"""MODE: {"extraction_summary" if mode == "extraction" else "follow_up"}
User Query: {json.dumps(user_request, ensure_ascii=False)}
Language hint: {language}

Recent history: {json.dumps(recent, ensure_ascii=False, separators=(",", ":")) if recent else "none"}

Dataset: {len(dataset)} rows; columns: {json.dumps(list(dataset[0].keys()) if dataset else [], ensure_ascii=False)}
Column statistics (whole dataset): {json.dumps(stats, ensure_ascii=False, separators=(",", ":"))}
Rows visible to you: {len(visible)} of {len(dataset)} ({"ALL rows are visible" if all_visible else "NOT all rows visible - use `query` to act on all rows"})
{json.dumps(visible, ensure_ascii=False, separators=(",", ":"))}
"""
        if input_data.get("uploaded_context") and mode != "extraction":
            prompt += f"\n<untrusted_source_content>\n{str(input_data['uploaded_context'])[:2000]}\n</untrusted_source_content>"

        response_text = await ai_router.generate(
            task_category="conversation", prompt=prompt, system_prompt=CONVERSATION_SYSTEM_PROMPT, temperature=0.4)

        try:
            data = extract_json(response_text, "object")
        except LLMInvalidOutputError:
            plain = response_text.strip()
            looks_json = plain[:1] in "{[" or "```" in plain
            data = {"response_text": "I couldn't format that answer. Please rephrase your question." if looks_json or not plain else plain[:1500]}

        result_rows: Optional[List[Dict[str, Any]]] = None
        ids = data.get("matching_row_ids")
        if isinstance(ids, list) and ids:
            picked = [dataset[i] for i in ids if isinstance(i, int) and 0 <= i < len(dataset)]
            result_rows = picked
        elif isinstance(data.get("query"), dict):
            result_rows = await asyncio.to_thread(apply_query, dataset, data["query"])
        elif isinstance(data.get("filtered_data"), list) and data["filtered_data"]:
            # Backwards compatibility with the old contract. Only rows that really exist in the dataset are accepted,
            # so a model can never invent result rows.
            result_rows = [r for r in data["filtered_data"][:500] if isinstance(r, dict) and r in dataset]

        export = str(data.get("export_requested", "none")).lower()
        export = export if export in VALID_EXPORTS else "none"
        text = str(data.get("response_text") or "").strip() or "Done."

        await redis_store.append_conversation_history(session_id, {"role": "user", "content": user_request})
        await redis_store.append_conversation_history(session_id, {"role": "assistant", "content": text})

        input_data["conversation_response"] = {
            "response_text": text,
            "export_requested": export,
            "result_count": None if result_rows is None else len(result_rows),
        }
        input_data["result_rows"] = None if result_rows is None else result_rows[: settings.CHAT_PREVIEW_ROWS]
        input_data["filtered_data"] = dataset if result_rows is None else result_rows   # ExportAgent compatibility
        input_data["export_requested"] = export
        logger.info(f"[{session_id}] Conversation done: mode={mode} result_rows={None if result_rows is None else len(result_rows)} export={export}")
        return input_data


conversation_agent = ConversationAgent()
