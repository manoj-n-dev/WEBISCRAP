from typing import Optional
from loguru import logger
from .providers.groq_client import groq_client
from .providers.gemini_client import gemini_client

class AIRouter:
    def __init__(self):
        # Define which provider handles which task category
        self.routing_rules = {
            "planning": "groq",
            "conversation": "groq",
            "validation": "groq",
            "intent": "groq",
            "analysis": "gemini",
            "extraction": "gemini",
            "cleaning": "gemini",
            "summarization": "gemini",
        }
        
    async def generate(
        self, 
        task_category: str, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        temperature: float = 0.7
    ) -> str:
        """
        Intelligently routes the prompt to the appropriate AI provider based on the task category.
        """
        provider_name = self.routing_rules.get(task_category)
        
        if not provider_name:
            logger.warning(f"Unknown task category '{task_category}', defaulting to Groq.")
            provider_name = "groq"
            
        try:
            if provider_name == "groq":
                return await groq_client.generate_response(
                    prompt=prompt, 
                    system_prompt=system_prompt,
                    temperature=temperature
                )
            elif provider_name == "gemini":
                return await gemini_client.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature
                )
        except Exception as e:
            # Simple Failover Logic
            logger.error(f"Primary provider {provider_name} failed for task '{task_category}': {str(e)}")
            fallback_provider = "gemini" if provider_name == "groq" else "groq"
            logger.info(f"Attempting failover to {fallback_provider}...")
            
            if fallback_provider == "groq":
                return await groq_client.generate_response(prompt=prompt, system_prompt=system_prompt, temperature=temperature)
            else:
                return await gemini_client.generate_response(prompt=prompt, system_prompt=system_prompt, temperature=temperature)

ai_router = AIRouter()
