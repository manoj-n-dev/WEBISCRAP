import time
from typing import List, Dict
from loguru import logger
from core.config import settings
from ai.errors import LLMRateLimitError, LLMUnavailableError


class KeyManager:
    def __init__(self, provider: str, keys: List[str]):
        self.provider = provider
        self.keys = keys
        # N8: Track cooldown per (key, model) tuple so 429 on one model doesn't block another.
        # An empty model string "" indicates a global key cooldown (e.g. 401/403 auth error).
        self.cooldowns: Dict[tuple, float] = {}
        self.usage_count: Dict[str, int] = {k: 0 for k in keys}
        self.errors: Dict[str, int] = {k: 0 for k in keys}

    def _is_key_active(self, key: str, model: str = "") -> bool:
        now = time.time()
        # Global key cooldown (e.g. invalid key credentials)
        if self.cooldowns.get((key, ""), 0) > now:
            return False
        # Model-specific cooldown (e.g. 429 rate limit on specific model)
        if model and self.cooldowns.get((key, model), 0) > now:
            return False
        return True

    def _get_active_keys(self, model: str = "") -> List[str]:
        return [k for k in self.keys if self._is_key_active(k, model)]

    def seconds_until_available(self, model: str = "") -> int:
        """Seconds until the soonest cooled-down key is usable (0 if one is usable now)."""
        if self._get_active_keys(model):
            return 0
        now = time.time()
        waits = []
        for k in self.keys:
            global_wait = self.cooldowns.get((k, ""), 0) - now
            model_wait = self.cooldowns.get((k, model), 0) - now if model else 0
            key_wait = max(global_wait, model_wait)
            if key_wait > 0:
                waits.append(key_wait)
        return max(1, int(min(waits))) if waits else 0

    def get_key(self, model: str = "") -> str:
        if not self.keys:
            raise LLMUnavailableError("No Groq API key is configured on the server.")
        active_keys = self._get_active_keys(model)
        if not active_keys:
            wait = self.seconds_until_available(model) or 60
            logger.error(f"No active keys for provider {self.provider} (model={model or 'all'}, retry in ~{wait}s)")
            raise LLMRateLimitError(
                f"All {self.provider} API keys are rate-limited right now for model {model or 'all'}.",
                retry_after=wait, scope="minute" if wait <= 120 else "day",
            )
        active_keys.sort(key=lambda k: self.usage_count.get(k, 0))
        selected_key = active_keys[0]
        self.usage_count[selected_key] = self.usage_count.get(selected_key, 0) + 1
        return selected_key

    def mark_key_exhausted(self, key: str, cooldown_seconds: int = 3600, model: str = ""):
        self.cooldowns[(key, model)] = time.time() + cooldown_seconds
        self.errors[key] = self.errors.get(key, 0) + 1
        model_desc = f" for model {model}" if model else " for all models"
        logger.warning(f"Marked {self.provider} key (…{key[-4:]}){model_desc} unavailable for {cooldown_seconds}s")


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
