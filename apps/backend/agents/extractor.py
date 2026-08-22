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
        
        if not dom_snapshots:
            logger.warning(f"[{session_id}] No DOM snapshots provided for extraction.")
            input_data["extracted_data"] = []
            return input_data
            
        all_extracted_data = []
        
        # We might have multiple snapshots (e.g. from pagination)
        # We'll process them one by one to avoid context length limits
        for i, html_chunk in enumerate(dom_snapshots):
            logger.info(f"[{session_id}] Extracting from snapshot {i+1}/{len(dom_snapshots)}")
            
            # Ensure we are not sending excessive tokens.
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
            
            response_text = await ai_router.generate(
                task_category="extraction",
                prompt=prompt,
                system_prompt=EXTRACTOR_SYSTEM_PROMPT,
                temperature=0.1
            )
            
            try:
                # Clean markdown block if present
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                    
                # Sometimes the model might wrap in a generic text instead of just an array
                match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if match:
                    response_text = match.group(0)
                    
                data = json.loads(response_text)
                if isinstance(data, list):
                    all_extracted_data.extend(data)
                elif isinstance(data, dict):
                    all_extracted_data.append(data)
                    
            except json.JSONDecodeError as e:
                logger.error(f"[{session_id}] Extractor failed to parse JSON for snapshot {i+1}. Skipping. Error: {e}. Output: {response_text[:200]}...")
                # Continue to next snapshot instead of failing the whole process
                continue
                
        input_data["extracted_data"] = all_extracted_data
        
        # To save memory, we can drop the raw DOM snapshots now
        if "dom_snapshots" in input_data:
            del input_data["dom_snapshots"]
            
        return input_data

extractor_agent = ExtractorAgent()
