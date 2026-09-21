import asyncio
import re
from typing import Dict, Optional, Tuple

import groq
from groq import AsyncGroq
from loguru import logger

from ai.errors import (
    LLMError, LLMInvalidOutputError, LLMRateLimitError,
    LLMRequestTooLargeError, LLMUnavailableError,
)
from ai.key_manager import ai_manager
from core.config import settings

_MAX_ATTEMPTS = 4
_DUR_RE = re.compile(r"(?:(\d+(?:\.\d+)?)h)?(?:(\d+(?:\.\d+)?)m(?!s))?(?:(\d+(?:\.\d+)?)s)?(?:(\d+(?:\.\d+)?)ms)?$")


def _parse_duration(text: str) -> Optional[float]:
    """'7.5s' -> 7.5, '1m30.5s' -> 90.5, '2h3m' -> 7380, '250ms' -> 0.25"""
    m = _DUR_RE.match(text.strip())
    if not m or not any(m.groups()):
        return None
    h, mi, s, ms = (float(g) if g else 0.0 for g in m.groups())
    return h * 3600 + mi * 60 + s + ms / 1000


def parse_rate_limit_error(exc: Exception) -> Tuple[int, str]:
    """Return (retry_after_seconds, scope) from a Groq 429 error. scope is 'minute' or 'day'."""
    message = str(getattr(exc, "message", "") or exc)
    headers = {}
    try:
        headers = dict(getattr(getattr(exc, "response", None), "headers", {}) or {})
    except Exception:
        pass
    retry_after: Optional[float] = None
    ra = headers.get("retry-after") or headers.get("Retry-After")
    if ra:
        try:
            retry_after = float(ra)
        except ValueError:
            retry_after = None
    if retry_after is None:
        m = re.search(r"try again in ([0-9hms.]+)", message, re.I)
        if m:
            retry_after = _parse_duration(m.group(1).rstrip("."))
    low = message.lower()
    scope = "day" if ("per day" in low or "(tpd)" in low or "(rpd)" in low) else "minute"
    if retry_after is None:
        retry_after = 3600 if scope == "day" else 30
    return int(max(1, round(retry_after))), scope


class GroqClient:
    def __init__(self):
        self.default_model = "openai/gpt-oss-120b"
        self._clients: Dict[str, AsyncGroq] = {}

    def _client_for(self, api_key: str) -> AsyncGroq:
        # Re-use one HTTP client per key (avoids a new TLS handshake + leaked connection per call)
        client = self._clients.get(api_key)
        if client is None:
            client = AsyncGroq(api_key=api_key, timeout=45.0, max_retries=0)
            self._clients[api_key] = client
        return client

    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        json_mode: bool = False,
        reasoning_effort: Optional[str] = "low",
    ) -> str:
        model_name = model or self.default_model
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        use_json_mode = json_mode
        waited = 0.0
        last_error: Optional[Exception] = None

        for attempt in range(_MAX_ATTEMPTS):
            try:
                api_key = ai_manager.groq_keys.get_key()
            except LLMRateLimitError as rl:
                # Short waits are absorbed here (rolling TPM window); long waits surface to the user.
                if rl.retry_after and rl.retry_after <= settings.LLM_MAX_WAIT_SECONDS and waited < 30:
                    await asyncio.sleep(rl.retry_after + 0.5)
                    waited += rl.retry_after + 0.5
                    continue
                raise

            kwargs = dict(messages=messages, model=model_name, temperature=temperature, max_tokens=max_tokens)
            if use_json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            if reasoning_effort and model_name.startswith("openai/gpt-oss"):
                kwargs["extra_body"] = {"reasoning_effort": reasoning_effort}

            try:
                logger.debug(f"Groq request model={model_name} key=…{api_key[-4:]} attempt={attempt + 1}")
                response = await self._client_for(api_key).chat.completions.create(**kwargs)
                choice = response.choices[0]
                content = choice.message.content or ""
                if not content.strip() and getattr(choice, "finish_reason", "") == "length":
                    raise LLMInvalidOutputError("The AI ran out of output space before answering. Try a smaller request.")
                return content

            except groq.RateLimitError as e:
                retry_after, scope = parse_rate_limit_error(e)
                logger.warning(f"Groq 429 ({scope}) key=…{api_key[-4:]} retry_after={retry_after}s: {getattr(e, 'message', e)}")
                cooldown = min(retry_after + 1, 3600 if scope == "day" else 120)
                ai_manager.groq_keys.mark_key_exhausted(api_key, cooldown_seconds=cooldown)
                last_error = LLMRateLimitError("The AI provider rate limit was reached.", retry_after=retry_after, scope=scope)
                continue

            except groq.APIStatusError as e:
                status = e.status_code
                msg = str(getattr(e, "message", "") or e)
                if status == 413:
                    logger.error(f"Groq 413 request too large: {msg[:300]}")
                    if "tokens per day" in msg.lower():
                        raise LLMRateLimitError("Daily AI token limit reached.", retry_after=3600, scope="day")
                    raise LLMRequestTooLargeError("This request is too large for the AI model right now. Try a smaller file/page.")
                if status in (401, 403):
                    logger.error(f"Groq auth error {status} for key …{api_key[-4:]}")
                    ai_manager.groq_keys.mark_key_exhausted(api_key, cooldown_seconds=3600)
                    last_error = LLMUnavailableError("The AI service credentials were rejected.")
                    continue
                if status == 400 and use_json_mode and ("response_format" in msg.lower() or "json" in msg.lower()):
                    logger.warning("JSON mode rejected by model; retrying without response_format")
                    use_json_mode = False
                    continue
                if status >= 500:
                    last_error = LLMUnavailableError("The AI service is temporarily unavailable.")
                    await asyncio.sleep(min(2 * (attempt + 1), 6))
                    continue
                logger.error(f"Groq API error {status}: {msg[:300]}")
                raise LLMError("The AI service rejected the request.")

            except (groq.APITimeoutError, groq.APIConnectionError) as e:
                logger.warning(f"Groq network error: {e}")
                last_error = LLMUnavailableError("The AI service timed out. Please try again.")
                await asyncio.sleep(min(2 * (attempt + 1), 6))
                continue

        if isinstance(last_error, LLMError):
            raise last_error
        raise LLMUnavailableError("The AI service is unavailable. Please try again shortly.")


groq_client = GroqClient()
