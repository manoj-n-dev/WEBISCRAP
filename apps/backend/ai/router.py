from typing import Optional
from loguru import logger
from .providers.groq_client import groq_client

# H13: Default max_tokens per task category — extraction/cleaning need more room
_DEFAULT_MAX_TOKENS = {
    "extraction": 8192,
    "cleaning": 8192,
    "planning": 4096,
    "conversation": 4096,
    "validation": 4096,
    "intent": 2048,
    "analysis": 4096,
    "summarization": 4096,
}

# C6: Split models across task categories for separate rate-limit buckets
TASK_MODEL_MAP = {
    "extraction": "openai/gpt-oss-120b",
    "cleaning": "openai/gpt-oss-120b",
    "planning": "openai/gpt-oss-20b",
    "conversation": "openai/gpt-oss-20b",
    "validation": "openai/gpt-oss-20b",
    "intent": "openai/gpt-oss-20b",
    "analysis": "openai/gpt-oss-20b",
    "summarization": "openai/gpt-oss-20b",
}

class AIRouter:
    def __init__(self):
        self.routing_rules = {
            "planning": "groq",
            "conversation": "groq",
            "validation": "groq",
            "intent": "groq",
            "analysis": "groq",
            "extraction": "groq",
            "cleaning": "groq",
            "summarization": "groq",
        }
        
    async def generate(
        self, 
        task_category: str, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Routes the prompt to the appropriate AI provider.
        M1: Removed the fake failover — groq_client already has @retry with tenacity.
        H13: max_tokens defaults per task category so extraction/cleaning aren't truncated.
        C6: Routes to dedicated models per task category to isolate Groq TPM/RPM limits.
        """
        provider_name = self.routing_rules.get(task_category)
        
        if not provider_name:
            logger.warning(f"Unknown task category '{task_category}', defaulting to Groq.")
            
        resolved_max_tokens = max_tokens or _DEFAULT_MAX_TOKENS.get(task_category, 4096)
        model_to_use = TASK_MODEL_MAP.get(task_category, "openai/gpt-oss-120b")
            
        return await groq_client.generate_response(
            prompt=prompt, 
            system_prompt=system_prompt,
            model=model_to_use,
            temperature=temperature,
            max_tokens=resolved_max_tokens,
        )

ai_router = AIRouter()
