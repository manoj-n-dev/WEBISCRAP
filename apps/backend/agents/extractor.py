from typing import Any, Dict, List

from loguru import logger

from ai.errors import LLMInvalidOutputError
from ai.router import ai_router
from core.config import settings
from core.llm_json import extract_records
from prompts.extractor_prompt import EXTRACTOR_SYSTEM_PROMPT
from .base import BaseAgent


def input_char_budget() -> int:
    """Max source characters per LLM call. Keeps (prompt + output) under Groq's free-tier 8K TPM."""
    return 20000 if settings.groq_is_paid_tier else 7000


def max_chunks() -> int:
    return 5 if settings.groq_is_paid_tier else 3


def split_text(text: str, size: int, limit: int) -> List[str]:
    return [text[i:i + size] for i in range(0, len(text), size)][:limit]


class ExtractorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ExtractorAgent")

    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        extraction_goal = input_data.get("extraction_goal", "Extract main content")
        expected_fields = input_data.get("expected_fields", [])
        dom_snapshots = input_data.get("dom_snapshots", [])
        uploaded_context = input_data.get("uploaded_context", "") or input_data.get("document_text", "")

        budget, chunk_limit = input_char_budget(), max_chunks()
        sources: List[str] = []
        if dom_snapshots:                                   # Mode A: web pages
            seen = set()
            for snap in dom_snapshots:
                key = hash(snap.strip())
                if key in seen:
                    continue
                seen.add(key)
                sources.extend(split_text(snap, budget, 2))  # keep items below the first slice instead of truncating
        elif uploaded_context:                              # Mode B: PDF / DOCX / image text
            sources = split_text(uploaded_context, budget, chunk_limit)
        else:
            logger.warning(f"[{session_id}] Neither DOM snapshots nor uploaded document context provided for extraction.")
        sources = sources[: max(chunk_limit, 3)]

        all_extracted: List[Dict[str, Any]] = []
        failures = 0
        for i, chunk in enumerate(sources):
            logger.info(f"[{session_id}] Extracting chunk {i + 1}/{len(sources)} ({len(chunk)} chars)")
            prompt = f"""
            User Extraction Goal: {extraction_goal}
            Expected Fields: {expected_fields}

            <untrusted_source_content>
            {chunk}
            </untrusted_source_content>
            """
            try:
                text = await ai_router.generate(task_category="extraction", prompt=prompt,
                                                system_prompt=EXTRACTOR_SYSTEM_PROMPT, temperature=0.1, json_mode=True)
                all_extracted.extend(extract_records(text))
            except LLMInvalidOutputError as e:
                failures += 1
                logger.error(f"[{session_id}] Extractor could not parse chunk {i + 1}: {e}")
            # LLMRateLimitError / LLMUnavailableError / LLMRequestTooLargeError propagate to the API (UI shows why).

        if sources and failures == len(sources):
            raise LLMInvalidOutputError("The AI could not structure this source. Try a narrower request.")

        input_data["extracted_data"] = all_extracted
        input_data.pop("dom_snapshots", None)
        return input_data


extractor_agent = ExtractorAgent()
