from typing import Any, Dict

from loguru import logger

from core.config import settings
from memory.session_store import redis_store
from .base import BaseAgent


class MemoryAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="MemoryAgent")

    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        action = input_data.get("action", "save")
        try:
            if action == "save":
                rows = input_data.get("cleaned_data", []) or []
                if not rows:
                    # Never overwrite a good dataset with an empty result (that wiped follow-ups before).
                    logger.warning(f"[{session_id}] MemoryAgent: empty result, keeping the previously saved dataset.")
                    return input_data
                total = len(rows)
                cached = {
                    "cleaned_data": rows[: settings.MAX_DATASET_ROWS],
                    "validation": input_data.get("validation", {}),
                    "target_url": input_data.get("target_url", ""),
                    "expected_fields": input_data.get("expected_fields", []),
                    "source_upload_ids": input_data.get("source_upload_ids", []),
                    "total_rows": total,
                    "truncated": total > settings.MAX_DATASET_ROWS,
                }
                await redis_store.save_session_data(session_id, cached)
                logger.info(f"[{session_id}] MemoryAgent saved {min(total, settings.MAX_DATASET_ROWS)} rows to cache.")
            elif action == "load":
                cached = await redis_store.get_session_data(session_id)
                if isinstance(cached, dict) and cached.get("cleaned_data"):
                    input_data.update(cached)
                    logger.info(f"[{session_id}] MemoryAgent loaded dataset from cache.")
                else:
                    logger.info(f"[{session_id}] MemoryAgent found no cached data.")
        except Exception as e:
            logger.error(f"[{session_id}] MemoryAgent failed to interact with Redis: {e}")
            input_data.setdefault("warnings", []).append(
                "Your results could not be saved, so follow-up questions may not work for this chat.")
        return input_data


memory_agent = MemoryAgent()
