import json
from typing import Dict, Any, List
from .base import BaseAgent
from ai.router import ai_router
from prompts.cleaner_prompt import CLEANER_SYSTEM_PROMPT
from loguru import logger
import re

class CleanerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="CleanerAgent")
        
    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        raw_data = input_data.get("extracted_data", [])
        target_url = input_data.get("target_url", "")
        
        if not raw_data:
            logger.warning(f"[{session_id}] No data provided to CleanerAgent.")
            input_data["cleaned_data"] = []
            return input_data
            
        logger.info(f"[{session_id}] Cleaning {len(raw_data)} items.")
        
        # We process in chunks if the array is too large
        chunk_size = 50
        all_cleaned = []
        
        for i in range(0, len(raw_data), chunk_size):
            chunk = raw_data[i:i + chunk_size]
            
            prompt = f"""
            Base URL: {target_url}
            
            Raw Data Array:
            ```json
            {json.dumps(chunk, indent=2)}
            ```
            """
            
            response_text = await ai_router.generate(
                task_category="cleaning",
                prompt=prompt,
                system_prompt=CLEANER_SYSTEM_PROMPT,
                temperature=0.1
            )
            
            try:
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                    
                match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if match:
                    response_text = match.group(0)
                    
                cleaned_chunk = json.loads(response_text)
                if isinstance(cleaned_chunk, list):
                    all_cleaned.extend(cleaned_chunk)
                    
            except json.JSONDecodeError as e:
                logger.error(f"[{session_id}] Cleaner failed to parse JSON. Error: {e}. Snippet: {response_text[:200]}")
                # Fallback: just use the raw uncleaned chunk
                all_cleaned.extend(chunk)
                
        # Final pass duplicate removal using python just in case
        unique_cleaned = []
        seen = set()
        for item in all_cleaned:
            # Hash dict by turning it into a frozenset of items
            # Convert inner dicts/lists to strings for hashing
            try:
                hashable = frozenset((k, str(v)) for k, v in item.items())
                if hashable not in seen:
                    seen.add(hashable)
                    unique_cleaned.append(item)
            except Exception:
                # If unhashable, just append it
                unique_cleaned.append(item)
                
        input_data["cleaned_data"] = unique_cleaned
        del input_data["extracted_data"] # Free up memory
        
        return input_data

cleaner_agent = CleanerAgent()
