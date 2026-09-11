from typing import Dict, Any, List
from loguru import logger
import time

from .planner import planner_agent
from .analyzer import analyzer_agent
from .browser import browser_agent
from .extractor import extractor_agent
from .cleaner import cleaner_agent
from .validator import validator_agent
from .memory_agent import memory_agent
from .conversation import conversation_agent
from .exporter import export_agent

from .base import validate_target_url
from memory.session_store import redis_store

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
        
        pipeline_state = {
            "user_request": user_request,
            "target_url": target_url,
            "owner_id": owner_id,
            "data": None,
            "metadata": {}
        }
        
        # C3: Fetch uploaded file context for this session if available
        if session_id:
            uploaded_ids = await redis_store.list_uploaded_context_ids(session_id)
            if uploaded_ids:
                contexts = []
                for file_id in uploaded_ids:
                    ctx = await redis_store.get_uploaded_context(session_id, file_id)
                    if ctx:
                        contexts.append(ctx)
                if contexts:
                    pipeline_state["uploaded_context"] = "\n\n---\n\n".join(contexts)[:8000]
        
        try:
            # 1. Start Planner
            completed_steps = ["plan"]
            await redis_store.set_pipeline_progress(session_id, "plan")
            pipeline_state = await self.planner.run(pipeline_state, session_id)
            
            is_new_scrape = pipeline_state.get("is_new_scrape", True)
            
            if is_new_scrape:
                # 2. Analyze
                await redis_store.set_pipeline_progress(session_id, "analyze")
                pipeline_state = await self.analyzer.run(pipeline_state, session_id)
                completed_steps.append("analyze")
                
                # 3. Browse / Fetch
                await redis_store.set_pipeline_progress(session_id, "browse")
                pipeline_state = await self.browser.run(pipeline_state, session_id)
                completed_steps.append("browse")
                
                # 4. Extract
                await redis_store.set_pipeline_progress(session_id, "extract")
                pipeline_state = await self.extractor.run(pipeline_state, session_id)
                completed_steps.append("extract")
                
                # 5. Clean
                await redis_store.set_pipeline_progress(session_id, "clean")
                pipeline_state = await self.cleaner.run(pipeline_state, session_id)
                completed_steps.append("clean")
                
                # 6. Validate
                await redis_store.set_pipeline_progress(session_id, "validate")
                pipeline_state = await self.validator.run(pipeline_state, session_id)
                completed_steps.append("validate")
                
                # 7. Save to Memory
                pipeline_state["action"] = "save"
                pipeline_state = await self.memory.run(pipeline_state, session_id)
            else:
                # 7b. Load from Memory (for follow-up questions)
                pipeline_state["action"] = "load"
                pipeline_state = await self.memory.run(pipeline_state, session_id)
                
            # M5: Store actual completed steps in state
            pipeline_state["completed_steps"] = completed_steps
                
            # 8. Conversation / Answer
            pipeline_state = await self.conversation.run(pipeline_state, session_id)
            
            # 9. Export if requested
            pipeline_state = await self.exporter.run(pipeline_state, session_id)
            
            await redis_store.clear_pipeline_progress(session_id)
            logger.info(f"[{session_id}] Pipeline completed successfully.")
            return {
                "status": "success",
                "message": "Pipeline completed.",
                "data": pipeline_state
            }
            
        except Exception as e:
            await redis_store.clear_pipeline_progress(session_id)
            import traceback
            tb = traceback.format_exc()
            error_msg = f"{type(e).__name__}: {str(e)}" if str(e) else type(e).__name__
            logger.error(f"[{session_id}] Pipeline failed:\n{tb}")
            return {
                "status": "error",
                "message": error_msg,
            }

orchestrator = PipelineOrchestrator()

