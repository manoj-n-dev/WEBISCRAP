import json
from typing import Dict, Any
from .base import BaseAgent
from ai.router import ai_router
from prompts.planner_prompt import PLANNER_SYSTEM_PROMPT
from loguru import logger

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="PlannerAgent")
        
    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        user_request = input_data.get("user_request", "")
        target_url = input_data.get("target_url", "")
        
        prompt = f"User Request: '{user_request}'\nTarget URL: '{target_url}'\nGenerate the plan."
        
        # Route to planning model (Groq)
        response_text = await ai_router.generate(
            task_category="planning",
            prompt=prompt,
            system_prompt=PLANNER_SYSTEM_PROMPT,
            temperature=0.2
        )
        
        try:
            # Clean response text in case the model wrapped it in markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            plan = json.loads(response_text)
            logger.info(f"[{session_id}] Planner generated plan: {plan}")
            
            # Merge plan into pipeline state (preserves target_url, user_request, etc.)
            input_data.update(plan)
            return input_data
        except json.JSONDecodeError as e:
            logger.error(f"[{session_id}] Planner failed to output valid JSON. Error: {e}. Snippet: {response_text[:200]}")
            raise ValueError("Planner output was not valid JSON.") from e

planner_agent = PlannerAgent()
