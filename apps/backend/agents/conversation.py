import json
from typing import Dict, Any
from .base import BaseAgent
from ai.router import ai_router
from prompts.conversation_prompt import CONVERSATION_SYSTEM_PROMPT
from loguru import logger
from memory.session_store import redis_store

class ConversationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ConversationAgent")
        
    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        user_request = input_data.get("user_request", "")
        detected_language = input_data.get("detected_language", "english")
        
        # Data might come from pipeline or from cache
        dataset = input_data.get("cleaned_data", [])
        
        # Get chat history
        history = await redis_store.get_conversation_history(session_id)
        
        logger.info(f"[{session_id}] ConversationAgent processing query: '{user_request}' in language: {detected_language}")
        
        # To avoid blowing up context, only send a sample of the data to the LLM if it's too big, 
        # or we might use a smaller subset or just schema if it's huge.
        # For this prototype, we'll send up to 100 items.
        sample_dataset = dataset[:100]
        
        prompt = f"""
        User Query: '{user_request}'
        Language: '{detected_language}'
        
        Conversation History:
        {json.dumps(history[-5:], indent=2) if history else "No previous history."}
        
        Dataset (Total items: {len(dataset)}, Showing first {len(sample_dataset)}):
        ```json
        {json.dumps(sample_dataset, indent=2)}
        ```
        """
        
        response_text = await ai_router.generate(
            task_category="conversation",
            prompt=prompt,
            system_prompt=CONVERSATION_SYSTEM_PROMPT,
            temperature=0.7 # Higher temp for natural language
        )
        
        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            response_data = json.loads(response_text)
            
            # Save the new message to history
            await redis_store.append_conversation_history(session_id, {"role": "user", "content": user_request})
            await redis_store.append_conversation_history(session_id, {"role": "assistant", "content": response_data.get("response_text", "")})
            
            input_data["conversation_response"] = response_data
            return input_data
            
        except json.JSONDecodeError as e:
            logger.error(f"[{session_id}] ConversationAgent failed to parse JSON. Output: {response_text}")
            
            # Fallback text response
            fallback = {
                "response_text": response_text,
                "filtered_data": dataset,
                "export_requested": "none"
            }
            await redis_store.append_conversation_history(session_id, {"role": "user", "content": user_request})
            await redis_store.append_conversation_history(session_id, {"role": "assistant", "content": response_text})
            
            input_data["conversation_response"] = fallback
            return input_data

conversation_agent = ConversationAgent()
