from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Any, Dict
from pydantic import BaseModel
from loguru import logger

from database.connection import get_session
from auth.dependencies import get_current_user
from models.user import User
from agents.orchestrator import orchestrator
from memory.session_store import redis_store
import uuid

router = APIRouter()

class ScrapeRequest(BaseModel):
    target_url: str
    extraction_goal: str

async def background_scrape_task(target_url: str, extraction_goal: str, session_id: str, owner_id: str):
    """Runs the extraction pipeline in the background."""
    try:
        result = await orchestrator.execute_pipeline(
            user_request=extraction_goal,
            target_url=target_url,
            session_id=session_id,
            owner_id=owner_id
        )
        # Store job status in Redis so it can be polled
        await redis_store.save_session_data(session_id, {
            "status": "done" if result.get("status") == "success" else "failed",
            "result": result
        })
    except Exception as e:
        logger.error(f"Background scrape job {session_id} failed: {e}", exc_info=True)
        await redis_store.save_session_data(session_id, {
            "status": "failed",
            "error": "An internal error occurred during extraction."
        })

@router.post("/", response_model=Dict[str, Any])
async def submit_scrape_job(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Submit a scraping job to run in the background. Useful for long-running extractions.
    """
    session_id = str(uuid.uuid4())
    
    # C2: Set session ownership before scheduling the background task
    await redis_store.set_session_owner(session_id, str(current_user.id))
    
    # Mark as pending initially
    await redis_store.save_session_data(session_id, {"status": "pending"})
    
    background_tasks.add_task(
        background_scrape_task, 
        request.target_url, 
        request.extraction_goal, 
        session_id,
        str(current_user.id)
    )
    
    return {
        "status": "accepted",
        "job_id": session_id,
        "message": "Scrape job submitted to background."
    }

@router.get("/{job_id}")
async def get_scrape_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Poll the status/result of a background scrape job.
    """
    # Ownership check
    owner_id = await redis_store.get_session_owner(job_id)
    if not owner_id or owner_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this job")
    
    data = await redis_store.get_session_data(job_id)
    if not data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return data
