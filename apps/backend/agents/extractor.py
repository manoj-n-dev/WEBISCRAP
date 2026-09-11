import json
from typing import Dict, Any, List
from .base import BaseAgent
from ai.router import ai_router
from prompts.extractor_prompt import EXTRACTOR_SYSTEM_PROMPT
from loguru import logger
import re

class ExtractorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ExtractorAgent")
        
    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        extraction_goal = input_data.get("extraction_goal", "Extract main content")
        expected_fields = input_data.get("expected_fields", [])
        dom_snapshots = input_data.get("dom_snapshots", [])
        uploaded_context = input_data.get("uploaded_context", "") or input_data.get("document_text", "")
        
        all_extracted_data = []

        # Mode A: Web DOM snapshots from browser
        if dom_snapshots:
            # H5: Deduplicate repeated snapshots across pagination to cut unnecessary LLM calls
            unique_snapshots = []
            seen_snapshots = set()
            for snap in dom_snapshots:
                snap_hash = hash(snap.strip())
                if snap_hash not in seen_snapshots:
                    seen_snapshots.add(snap_hash)
                    unique_snapshots.append(snap)

            for i, html_chunk in enumerate(unique_snapshots):
                logger.info(f"[{session_id}] Extracting from DOM snapshot {i+1}/{len(unique_snapshots)}")
                if len(html_chunk) > 20000:
                    html_chunk = html_chunk[:20000]
                    
                prompt = f"""
                Extraction Goal: {extraction_goal}
                Expected Fields: {expected_fields}
                
                HTML Content:
                ```html
                {html_chunk}
                ```
                """
                extracted = await self._run_extraction_prompt(prompt, session_id, f"snapshot {i+1}")
                all_extracted_data.extend(extracted)

        # Mode B: Document / text extraction (PDF, DOCX, CSV, spreadsheets, text)
        elif uploaded_context:
            logger.info(f"[{session_id}] Extracting from uploaded document context ({len(uploaded_context)} chars)")
            # Chunk document context into segments if needed (up to 20,000 chars each)
            chunk_size = 20000
            chunks = [uploaded_context[i:i+chunk_size] for i in range(0, len(uploaded_context), chunk_size)]
            for i, doc_chunk in enumerate(chunks[:5]): # Up to 5 chunks
                prompt = f"""
                Extraction Goal: {extraction_goal}
                Expected Fields: {expected_fields}
                
                Document / Text Content:
                ```text
                {doc_chunk}
                ```
                """
                extracted = await self._run_extraction_prompt(prompt, session_id, f"doc chunk {i+1}")
                all_extracted_data.extend(extracted)
        else:
            logger.warning(f"[{session_id}] Neither DOM snapshots nor uploaded document context provided for extraction.")

        input_data["extracted_data"] = all_extracted_data
        
        # To save memory, drop raw DOM snapshots
        if "dom_snapshots" in input_data:
            del input_data["dom_snapshots"]
            
        return input_data

    async def _run_extraction_prompt(self, prompt: str, session_id: str, label: str) -> List[Dict[str, Any]]:
        """Helper to call router and parse structured JSON list."""
        try:
            response_text = await ai_router.generate(
                task_category="extraction",
                prompt=prompt,
                system_prompt=EXTRACTOR_SYSTEM_PROMPT,
                temperature=0.1
            )
            
            # Clean markdown block if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if match:
                response_text = match.group(0)
                
            data = json.loads(response_text)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            return []
        except Exception as e:
            logger.error(f"[{session_id}] Extractor failed to parse JSON for {label}: {e}")
            return []

extractor_agent = ExtractorAgent()
