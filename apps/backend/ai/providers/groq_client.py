import asyncio
from groq import AsyncGroq, APIStatusError, APITimeoutError
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ai.key_manager import ai_manager

class GroqClient:
    def __init__(self):
        self.default_model = "llama-3.3-70b-versatile"
        
    def _get_client(self) -> AsyncGroq:
        api_key = ai_manager.groq_keys.get_key()
        return AsyncGroq(api_key=api_key), api_key

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIStatusError, APITimeoutError))
    )
    async def generate_response(self, prompt: str, system_prompt: str = None, model: str = None, temperature: float = 0.7) -> str:
        client, used_key = self._get_client()
        model_name = model or self.default_model
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            logger.debug(f"Sending request to Groq ({model_name}) using key ending in {used_key[-4:]}")
            response = await client.chat.completions.create(
                messages=messages,
                model=model_name,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except APIStatusError as e:
            if e.status_code == 429: # Rate limit
                logger.warning(f"Groq rate limit hit for key ending in {used_key[-4:]}")
                ai_manager.groq_keys.mark_key_exhausted(used_key, cooldown_seconds=60)
            raise e
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise e

groq_client = GroqClient()
