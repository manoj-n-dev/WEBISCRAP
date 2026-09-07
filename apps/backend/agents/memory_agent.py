from typing import Dict, Any
from .base import BaseAgent
from loguru import logger
from memory.session_store import redis_store

class MemoryAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="MemoryAgent")
        
    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        action = input_data.get("action", "save")
        
        try:
            if action == "save":
                # We save the cleaned data and the validation results to cache
                data_to_cache = {
                    "cleaned_data": input_data.get("cleaned_data", []),
                    "validation": input_data.get("validation", {}),
                    "target_url": input_data.get("target_url", ""),
                    "expected_fields": input_data.get("expected_fields", [])
                }
                await redis_store.save_session_data(session_id, data_to_cache)
                logger.info(f"[{session_id}] MemoryAgent saved dataset to cache.")
                
            elif action == "load":
                cached = await redis_store.get_session_data(session_id)
                if cached:
                    input_data.update(cached)
                    logger.info(f"[{session_id}] MemoryAgent loaded dataset from cache.")
                else:
                    logger.info(f"[{session_id}] MemoryAgent found no cached data.")
                    
        except Exception as e:
            logger.error(f"[{session_id}] MemoryAgent failed to interact with Redis: {e}")
            # Non-fatal error, the conversation agent will just proceed with whatever data it has in memory
            
        return input_data

memory_agent = MemoryAgent()
