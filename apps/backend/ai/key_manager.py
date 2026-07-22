import asyncio
import random
import time
from typing import List, Dict, Optional
from loguru import logger
from core.config import settings

class KeyManager:
    def __init__(self, provider: str, keys: List[str]):
        self.provider = provider
        self.keys = keys
        # Track usage and status
        self.key_status: Dict[str, Dict] = {
            key: {
                "active": True,
                "cooldown_until": 0,
                "usage_count": 0,
                "errors": 0
            }
            for key in keys
        }
        
    def _get_active_keys(self) -> List[str]:
        now = time.time()
        active = []
        for key, status in self.key_status.items():
            if status["active"]:
                active.append(key)
            elif status["cooldown_until"] > 0 and now > status["cooldown_until"]:
                # Cooldown expired, reactive key
                status["active"] = True
                status["cooldown_until"] = 0
                active.append(key)
        return active

    def get_key(self) -> str:
        active_keys = self._get_active_keys()
        if not active_keys:
            logger.error(f"No active keys available for provider {self.provider}")
            raise Exception(f"API Rate Limit: All {self.provider} keys are exhausted or on cooldown.")
            
        # Select key with lowest usage count (basic load balancing)
        active_keys.sort(key=lambda k: self.key_status[k]["usage_count"])
        selected_key = active_keys[0]
        
        # Increment usage
        self.key_status[selected_key]["usage_count"] += 1
        return selected_key

    def mark_key_exhausted(self, key: str, cooldown_seconds: int = 3600):
        """Mark a key as rate-limited or exhausted, putting it on cooldown."""
        if key in self.key_status:
            self.key_status[key]["active"] = False
            self.key_status[key]["cooldown_until"] = time.time() + cooldown_seconds
            self.key_status[key]["errors"] += 1
            logger.warning(f"Marked {self.provider} key (ending in {key[-4:]}) as exhausted. Cooldown: {cooldown_seconds}s")

class AIManager:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        self.groq_keys = KeyManager("Groq", settings.groq_keys_list)
        logger.info(f"Initialized AIManager with {len(self.groq_keys.keys)} Groq keys.")

ai_manager = AIManager.get_instance()
