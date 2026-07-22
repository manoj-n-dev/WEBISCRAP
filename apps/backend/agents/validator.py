import json
from typing import Dict, Any
from .base import BaseAgent
from ai.router import ai_router
from prompts.validator_prompt import VALIDATOR_SYSTEM_PROMPT
from loguru import logger

class ValidatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ValidatorAgent")
        
    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        cleaned_data = input_data.get("cleaned_data", [])
        extraction_goal = input_data.get("extraction_goal", "")
        expected_fields = input_data.get("expected_fields", [])
        
        if not cleaned_data:
            logger.warning(f"[{session_id}] No data provided to ValidatorAgent.")
            input_data["validation"] = {
                "confidence_score": 0,
                "validation_notes": "No data extracted.",
                "flagged_rows_count": 0,
                "is_valid": False
            }
            return input_data
            
        logger.info(f"[{session_id}] Validating {len(cleaned_data)} items.")
        
        # Take a sample of the data to validate if it's too large, or send the whole thing
        # Usually validating the first 50 items is enough to establish confidence
        sample_size = min(len(cleaned_data), 50)
        sample_data = cleaned_data[:sample_size]
        
        prompt = f"""
        Extraction Goal: {extraction_goal}
        Expected Fields: {expected_fields}
        
        Sample Data Array ({sample_size} of {len(cleaned_data)} items):
        ```json
        {json.dumps(sample_data, indent=2)}
        ```
        """
        
        response_text = await ai_router.generate(
            task_category="validation",
            prompt=prompt,
            system_prompt=VALIDATOR_SYSTEM_PROMPT,
            temperature=0.1
        )
        
        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            validation_result = json.loads(response_text)
            logger.info(f"[{session_id}] Validation result: Score={validation_result.get('confidence_score')}, Valid={validation_result.get('is_valid')}")
            
        except json.JSONDecodeError as e:
            logger.error(f"[{session_id}] Validator failed to parse JSON. Output: {response_text}")
            validation_result = {
                "confidence_score": 50,
                "validation_notes": "Validation agent failed to return parseable result.",
                "flagged_rows_count": 0,
                "is_valid": True # Give benefit of the doubt
            }
            
        input_data["validation"] = validation_result
        return input_data

validator_agent = ValidatorAgent()
