import asyncio
from groq import AsyncGroq, APIStatusError, APITimeoutError
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from typing import Optional, Tuple

from ai.key_manager import ai_manager

class GroqClient:
    def __init__(self):
        self.default_model = "openai/gpt-oss-120b"
        
    def _get_client(self) -> Tuple[AsyncGroq, str]:
        api_key = ai_manager.groq_keys.get_key()
        return AsyncGroq(api_key=api_key), api_key

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIStatusError, APITimeoutError))
    )
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        model: Optional[str] = None, 
        temperature: float = 0.7, 
        max_tokens: int = 4096
    ) -> str:
        client, used_key = self._get_client()
        model_name = model or self.default_model
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            logger.debug(f"Sending request to Groq ({model_name}) using key ending in {used_key[-4:]}")
            raw_response = await client.chat.completions.with_raw_response.create(
                messages=messages,
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            # C6: Log response rate-limit headers to observe real quota headroom
            headers = raw_response.headers
            rem_tokens = headers.get("x-ratelimit-remaining-tokens")
            rem_reqs = headers.get("x-ratelimit-remaining-requests")
            if rem_tokens or rem_reqs:
                logger.debug(f"Groq ({model_name}) limits — remaining tokens: {rem_tokens}, remaining requests: {rem_reqs}")
            parsed = raw_response.parse()
            response = await parsed if asyncio.iscoroutine(parsed) else parsed
            return response.choices[0].message.content or ""
        except APIStatusError as e:
            logger.error(f"Groq API error (status={e.status_code}): {e.message}")
            if e.status_code == 429: # Rate limit
                logger.warning(f"Groq rate limit hit for key ending in {used_key[-4:]}")
                ai_manager.groq_keys.mark_key_exhausted(used_key, cooldown_seconds=60)
            elif e.status_code in (413, 400): # Payload too large or bad request
                logger.error(f"Groq payload error — likely context window exceeded. Prompt too long.")
            raise e
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise e

groq_client = GroqClient()
