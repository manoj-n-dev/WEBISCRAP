from typing import Dict, Any, List
from loguru import logger
import time

from .planner import planner_agent
from .analyzer import analyzer_agent
from .browser import browser_agent
from .extractor import extractor_agent
from .cleaner import cleaner_agent
from .validator import validator_agent
from .memory import memory_agent
from .conversation import conversation_agent
from .exporter import export_agent

from .base import validate_target_url

class PipelineOrchestrator:
    """
    Coordinates the 9-agent pipeline for WEBISCRAP.
    """
    
    def __init__(self):
        self.planner = planner_agent
        self.analyzer = analyzer_agent
        self.browser = browser_agent
        self.extractor = extractor_agent
        self.cleaner = cleaner_agent
        self.validator = validator_agent
        self.memory = memory_agent
        self.conversation = conversation_agent
        self.exporter = export_agent

    async def execute_pipeline(self, user_request: str, target_url: str, session_id: str, owner_id: str = "") -> Dict[str, Any]:
        """
        Executes the full extraction pipeline or routes to conversation agent if data is cached.
        """
        logger.info(f"[{session_id}] Starting pipeline for URL: {target_url}")
        
        # SSRF protection
        if target_url and not validate_target_url(target_url):
            raise ValueError(f"Invalid or restricted target URL: {target_url}")
        
        # In a real execution, we would:
        # 1. Check if we already have extracted this URL in the current session (Memory Agent)
        # 2. If Yes, and user is just asking follow-up questions -> route to Conversation Agent
        # 3. If No, or it's a new extraction request -> run the full pipeline (1 -> 6)
        
        pipeline_state = {
            "user_request": user_request,
            "target_url": target_url,
            "owner_id": owner_id,
            "data": None,
            "metadata": {}
        }
        
        try:
            # 1. Start Planner
            await redis_store.redis.setex(f"pipeline_progress:{session_id}", 3600, "plan")
            pipeline_state = await self.planner.run(pipeline_state, session_id)
            
            is_new_scrape = pipeline_state.get("is_new_scrape", True)
            
            if is_new_scrape:
                # 2. Analyze
                await redis_store.redis.setex(f"pipeline_progress:{session_id}", 3600, "analyze")
                pipeline_state = await self.analyzer.run(pipeline_state, session_id)
                
                # 3. Browse / Fetch
                await redis_store.redis.setex(f"pipeline_progress:{session_id}", 3600, "browse")
                pipeline_state = await self.browser.run(pipeline_state, session_id)
                
                # 4. Extract
                await redis_store.redis.setex(f"pipeline_progress:{session_id}", 3600, "extract")
                pipeline_state = await self.extractor.run(pipeline_state, session_id)
                
                # 5. Clean
                await redis_store.redis.setex(f"pipeline_progress:{session_id}", 3600, "clean")
                pipeline_state = await self.cleaner.run(pipeline_state, session_id)
                
                # 6. Validate
                await redis_store.redis.setex(f"pipeline_progress:{session_id}", 3600, "validate")
                pipeline_state = await self.validator.run(pipeline_state, session_id)
                
                # 7. Save to Memory
                pipeline_state["action"] = "save"
                pipeline_state = await self.memory.run(pipeline_state, session_id)
            else:
                # 7b. Load from Memory (for follow-up questions)
                pipeline_state["action"] = "load"
                pipeline_state = await self.memory.run(pipeline_state, session_id)
                
            # 8. Conversation / Answer
            pipeline_state = await self.conversation.run(pipeline_state, session_id)
            
            # 9. Export if requested
            pipeline_state = await self.exporter.run(pipeline_state, session_id)
            
            await redis_store.redis.delete(f"pipeline_progress:{session_id}")
            logger.info(f"[{session_id}] Pipeline completed successfully.")
            return {
                "status": "success",
                "message": "Pipeline completed.",
                "data": pipeline_state
            }
            
        except Exception as e:
            await redis_store.redis.delete(f"pipeline_progress:{session_id}")
            import traceback
            tb = traceback.format_exc()
            error_msg = f"{type(e).__name__}: {str(e)}" if str(e) else type(e).__name__
            logger.error(f"[{session_id}] Pipeline failed:\n{tb}")
            return {
                "status": "error",
                "message": error_msg,
            }

orchestrator = PipelineOrchestrator()
