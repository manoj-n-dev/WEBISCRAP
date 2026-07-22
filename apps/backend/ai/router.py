from typing import Optional
from loguru import logger
from .providers.groq_client import groq_client

class AIRouter:
    def __init__(self):
        # Define which provider handles which task category
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
            return await groq_client.generate_response(
                prompt=prompt, 
                system_prompt=system_prompt,
                temperature=temperature
            )
        except Exception as e:
            # Simple Failover Logic using Groq only
            logger.error(f"Provider {provider_name} failed for task '{task_category}': {str(e)}")
            logger.info("Attempting retry on Groq...")
            
            return await groq_client.generate_response(prompt=prompt, system_prompt=system_prompt, temperature=temperature)

ai_router = AIRouter()
