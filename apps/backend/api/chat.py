import re
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from agents.orchestrator import PipelineInputError, orchestrator
from ai.errors import LLMError
from auth.dependencies import get_current_user
from database.connection import get_session
from memory.session_store import redis_store
from models.user import User

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field("", max_length=4000)
    target_url: str = Field("", max_length=2048)
    session_id: Optional[str] = Field(None, max_length=64)   # client-generated UUID (or None / "new")


_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def _valid_session_id(value: str) -> bool:
    """Client-generated UUIDs (and legacy ids). The whitelist keeps Redis keys clean; ownership is enforced separately."""
    return bool(value) and bool(_SESSION_ID_RE.match(value))


async def _require_owner(session_id: str, user: User, what: str) -> None:
    owner_id = await redis_store.get_session_owner(session_id)
    if not owner_id or owner_id != str(user.id):
        raise HTTPException(status_code=403, detail=f"Not authorized to access this session {what}")


@router.post("/", response_model=Dict[str, Any])
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> Any:
    """Main chat endpoint. The client generates the session UUID BEFORE the first message so that live pipeline
    progress can be polled from the very first run and uploads can be attached to the same session."""
    user_id = str(current_user.id)
    session_id = request.session_id
    if not session_id or session_id == "new":
        session_id = str(uuid.uuid4())
    elif not _valid_session_id(session_id):
        raise HTTPException(status_code=400, detail="Invalid session id")

    if not await redis_store.claim_session(session_id, user_id):     # atomic SET NX: no hijacking of someone else's id
        raise HTTPException(status_code=403, detail="Not authorized to access this session")

    await redis_store.add_user_session(user_id, session_id)           # also refreshes recency
    await redis_store.set_session_title_if_missing(session_id, request.message or request.target_url)

    try:
        result = await orchestrator.execute_pipeline(
            user_request=request.message, target_url=request.target_url,
            session_id=session_id, owner_id=user_id)
        result["session_id"] = session_id
        return result
    except PipelineInputError as e:
        raise HTTPException(status_code=400, detail={"code": e.code, "message": e.message})
    except LLMError as e:
        logger.warning(f"[{session_id}] LLM error surfaced to client: {e.code}")
        headers = {"Retry-After": str(e.retry_after)} if e.retry_after else None
        return JSONResponse(status_code=e.http_status, content={"detail": e.to_detail()}, headers=headers)
    except Exception as e:
        logger.error(f"Chat endpoint error for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred. Please try again.")


@router.get("/sessions", name="list_sessions")
async def list_sessions(current_user: User = Depends(get_current_user)) -> Any:
    """List all sessions of the current user (id, title, timestamp) for the sidebar."""
    return {"sessions": await redis_store.get_user_sessions(str(current_user.id))}


@router.get("/{session_id}/history")
async def get_chat_history(session_id: str, current_user: User = Depends(get_current_user)) -> Any:
    await _require_owner(session_id, current_user, "history")
    return {"history": await redis_store.get_conversation_history(session_id)}


@router.get("/{session_id}/data")
async def get_session_data(
    session_id: str,
    limit: Optional[int] = Query(None, ge=1, le=10000),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Cached dataset for a session. `limit` returns only a preview (used when re-opening a chat)."""
    await _require_owner(session_id, current_user, "data")
    data = await redis_store.get_session_data(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="No data found for this session")
    if limit and isinstance(data, dict) and isinstance(data.get("cleaned_data"), list):
        total = data.get("total_rows") or len(data["cleaned_data"])
        data = {**data, "cleaned_data": data["cleaned_data"][:limit], "total_rows": total}
    return data


@router.get("/{session_id}/progress")
async def get_pipeline_progress(session_id: str, current_user: User = Depends(get_current_user)) -> Any:
    # Fail-closed: an unowned/foreign session is 403. (For a brand-new chat the first poll can race the first POST;
    # the frontend treats that 403 as "not started yet" and simply polls again.)
    owner_id = await redis_store.get_session_owner(session_id)
    if not owner_id or owner_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this session progress")
    return {"step": await redis_store.get_pipeline_progress(session_id)}


@router.delete("/{session_id}")
async def delete_session(session_id: str, current_user: User = Depends(get_current_user)) -> Any:
    """Delete a chat (history, dataset, uploads) and remove it from the user's list."""
    await _require_owner(session_id, current_user, "")
    await redis_store.delete_session(session_id)
    return {"status": "deleted", "session_id": session_id}
