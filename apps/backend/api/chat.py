from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Any, Dict, Optional
from pydantic import BaseModel
from loguru import logger

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
        await redis_store.set_session_owner(session_id, str(current_user.id))
    else:
        # C1: Ownership check — prevent IDOR across sessions
        owner_id = await redis_store.get_session_owner(session_id)
        if owner_id and owner_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to access this session")
        
    try:
        # Pass to the orchestrator pipeline
        result = await orchestrator.execute_pipeline(
            user_request=request.message,
            target_url=request.target_url,
            session_id=session_id,
            owner_id=current_user.id
        )
        
        # Add the session_id to the response so frontend can maintain state
        result["session_id"] = session_id
        return result
        
    except Exception as e:
        # C8: Never leak internal errors to clients
        logger.error(f"Chat endpoint error for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred. Please try again.")

@router.get("/{session_id}/history")
async def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve conversation history for a specific session.
    """
    owner_id = await redis_store.get_session_owner(session_id)
    if owner_id and owner_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this session history")
        
    history = await redis_store.get_conversation_history(session_id)
    return {"history": history}

@router.get("/{session_id}/data")
async def get_session_data(
    session_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    H6: Retrieve the cached extraction data for a session (used by dataset view).
    """
    owner_id = await redis_store.get_session_owner(session_id)
    if owner_id and owner_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this session data")
    
    data = await redis_store.get_session_data(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="No data found for this session")
    
    return data

@router.get("/sessions", name="list_sessions")
async def list_sessions(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    H9: List all sessions belonging to the current user (for sidebar).
    """
    sessions = await redis_store.get_user_sessions(str(current_user.id))
    return {"sessions": sessions}

