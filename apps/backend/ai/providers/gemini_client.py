import asyncio
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google.api_core.exceptions import ResourceExhausted, RetryError
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ai.key_manager import ai_manager

class GeminiClient:
    def __init__(self):
        self.default_model = "gemini-3.5-flash"
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
    def _configure_client(self) -> str:
        api_key = ai_manager.gemini_keys.get_key()
        genai.configure(api_key=api_key)
        return api_key

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ResourceExhausted, RetryError))
    )
    async def generate_response(self, prompt: str, system_prompt: str = None, model: str = None, temperature: float = 0.4) -> str:
        used_key = self._configure_client()
        model_name = model or self.default_model
        
        try:
            logger.debug(f"Sending request to Gemini ({model_name}) using key ending in {used_key[-4:]}")
            
            # Use GenerativeModel directly for generation
            gen_model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_prompt if system_prompt else None,
                safety_settings=self.safety_settings
            )
            
            generation_config = genai.types.GenerationConfig(temperature=temperature)
            
            # Note: The official python SDK allows async via generate_content_async
            response = await gen_model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            return response.text
            
        except ResourceExhausted as e:
            logger.warning(f"Gemini rate limit hit for key ending in {used_key[-4:]}")
            ai_manager.gemini_keys.mark_key_exhausted(used_key, cooldown_seconds=60)
            raise e
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise e

gemini_client = GeminiClient()
