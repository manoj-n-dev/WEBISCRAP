import time
from typing import List, Dict
from loguru import logger
from core.config import settings
from ai.errors import LLMRateLimitError, LLMUnavailableError


class KeyManager:
    def __init__(self, provider: str, keys: List[str]):
        self.provider = provider
        self.keys = keys
        self.key_status: Dict[str, Dict] = {
            key: {"active": True, "cooldown_until": 0, "usage_count": 0, "errors": 0}
            for key in keys
        }

    def _get_active_keys(self) -> List[str]:
        now = time.time()
        active = []
        for key, status in self.key_status.items():
            if status["active"]:
                active.append(key)
            elif status["cooldown_until"] > 0 and now > status["cooldown_until"]:
                status["active"] = True
                status["cooldown_until"] = 0
                active.append(key)
        return active

    def seconds_until_available(self) -> int:
        """Seconds until the soonest cooled-down key is usable (0 if one is usable now)."""
        if self._get_active_keys():
            return 0
        now = time.time()
        waits = [s["cooldown_until"] - now for s in self.key_status.values() if s["cooldown_until"] > 0]
        return max(1, int(min(waits))) if waits else 0

    def get_key(self) -> str:
        if not self.keys:
            raise LLMUnavailableError("No Groq API key is configured on the server.")
        active_keys = self._get_active_keys()
        if not active_keys:
            wait = self.seconds_until_available() or 60
            logger.error(f"No active keys for provider {self.provider} (retry in ~{wait}s)")
            raise LLMRateLimitError(
                f"All {self.provider} API keys are rate-limited right now.",
                retry_after=wait, scope="minute" if wait <= 120 else "day",
            )
        active_keys.sort(key=lambda k: self.key_status[k]["usage_count"])
        selected_key = active_keys[0]
        self.key_status[selected_key]["usage_count"] += 1
        return selected_key

    def mark_key_exhausted(self, key: str, cooldown_seconds: int = 3600):
        if key in self.key_status:
            self.key_status[key]["active"] = False
            self.key_status[key]["cooldown_until"] = time.time() + cooldown_seconds
            self.key_status[key]["errors"] += 1
            logger.warning(f"Marked {self.provider} key (…{key[-4:]}) unavailable for {cooldown_seconds}s")


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
