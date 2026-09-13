from fastapi import APIRouter, Depends, HTTPException
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
        # C5: Store job status in dedicated Redis key namespace so it doesn't collide with session dataset
        await redis_store.save_job_status(session_id, {
            "status": "done" if result.get("status") == "success" else "failed",
            "result": result
        })
    except Exception as e:
        logger.error(f"Background scrape job {session_id} failed: {e}", exc_info=True)
        await redis_store.save_job_status(session_id, {
            "status": "failed",
            "error": "An internal error occurred during extraction."
        })

@router.post("/", response_model=Dict[str, Any])
async def submit_scrape_job(
    request: ScrapeRequest,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    H-05: Submit a scraping job to run in the durable Redis background queue.
    Job persists across server restarts and Render recycling.
    """
    session_id = str(uuid.uuid4())
    
    # Set session ownership before scheduling
    await redis_store.set_session_owner(session_id, str(current_user.id))
    # Track session under user for sidebar listing
    await redis_store.add_user_session(str(current_user.id), session_id)
    
    # Enqueue in durable Redis job queue
    job_payload = {
        "job_id": session_id,
        "target_url": request.target_url,
        "extraction_goal": request.extraction_goal,
        "owner_id": str(current_user.id),
    }
    await redis_store.enqueue_scrape_job(job_payload)
    
    return {
        "status": "accepted",
        "job_id": session_id,
        "message": "Scrape job enqueued to durable background queue."
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
    
    # C5: Read from job status namespace
    data = await redis_store.get_job_status(job_id)
    if not data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return data
