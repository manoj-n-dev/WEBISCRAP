from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Any, Dict, Optional
from pydantic import BaseModel

from database.connection import get_session
from auth.dependencies import get_current_user
from models.user import User
from agents.orchestrator import orchestrator
from memory.session_store import redis_store
import uuid

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    target_url: str = ""
    session_id: Optional[str] = None # If none, a new session is created

@router.post("/", response_model=Dict[str, Any])
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Main chat endpoint. Receives user message and optional URL, and routes through the 9-agent pipeline.
    """
    session_id = request.session_id
    if not session_id:
        session_id = str(uuid.uuid4())
        
    try:
        # Pass to the orchestrator pipeline
        result = await orchestrator.execute_pipeline(
            user_request=request.message,
            target_url=request.target_url,
            session_id=session_id
        )
        
        # Add the session_id to the response so frontend can maintain state
        result["session_id"] = session_id
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/history")
async def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve conversation history for a specific session.
    """
    history = await redis_store.get_conversation_history(session_id)
    return {"history": history}
