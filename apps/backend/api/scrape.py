from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Any, Dict
from pydantic import BaseModel

from database.connection import get_session
from auth.dependencies import get_current_user
from models.user import User
from agents.orchestrator import orchestrator
import uuid

router = APIRouter()

class ScrapeRequest(BaseModel):
    target_url: str
    extraction_goal: str

async def background_scrape_task(target_url: str, extraction_goal: str, session_id: str):
    # This runs asynchronously in the background
    await orchestrator.execute_pipeline(
        user_request=extraction_goal,
        target_url=target_url,
        session_id=session_id
    )

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
    
    # Add to FastAPI background tasks (or Celery in a heavier setup)
    background_tasks.add_task(
        background_scrape_task, 
        request.target_url, 
        request.extraction_goal, 
        session_id
    )
    
    return {
        "status": "accepted",
        "job_id": session_id,
        "message": "Scrape job submitted to background."
    }
