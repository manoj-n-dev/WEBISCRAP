import json
import asyncio
import redis.asyncio as redis
from typing import Dict, Any, Optional, List
from core.config import settings
from loguru import logger
import time

class RedisStore:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._loop = None

    async def connect(self):
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if self.redis_client is None or self._loop != current_loop:
            if self.redis_client is not None:
                try:
                    await self.redis_client.aclose()
                except Exception:
                    pass
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                health_check_interval=30,
                retry_on_timeout=True
            )
            self._loop = current_loop
            logger.info("Connected to Redis.")

    async def close(self):
        """Close connection and reset loop tracking."""
        if self.redis_client is not None:
            try:
                await self.redis_client.aclose()
            except Exception:
                pass
            self.redis_client = None
            self._loop = None

    @property
    def client(self) -> redis.Redis:
        """Return the active Redis client, raising an error if not connected."""
        if self.redis_client is None:
            raise RuntimeError("Redis client is not connected. Call connect() first.")
        return self.redis_client

    async def delete(self, *keys: str):
        """Delete one or more keys from Redis."""
        await self.connect()
        if self.redis_client and keys:
            await self.client.delete(*keys)

    async def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        await self.connect()
        data = await self.client.get(f"session:{session_id}:data")
        if data:
            return json.loads(data)
        return None

    async def save_session_data(self, session_id: str, data: Dict[str, Any], ttl_seconds: int = 86400):
        await self.connect()
        await self.client.set(
            f"session:{session_id}:data",
            json.dumps(data),
            ex=ttl_seconds
        )
        logger.info(f"[{session_id}] Session data saved to Redis with {ttl_seconds}s TTL.")

    async def set_session_owner(self, session_id: str, owner_id: str, ttl_seconds: int = 86400):
        await self.connect()
        await self.client.set(
            f"session:{session_id}:owner",
            owner_id,
            ex=ttl_seconds
        )

    async def get_session_owner(self, session_id: str) -> Optional[str]:
        await self.connect()
        return await self.client.get(f"session:{session_id}:owner")

    async def append_conversation_history(self, session_id: str, message: Dict[str, str]):
        await self.connect()
        key = f"session:{session_id}:history"
        await self.client.rpush(key, json.dumps(message))  # type: ignore[misc]
        await self.client.expire(key, 86400) # Keep history for 1 day

    async def get_conversation_history(self, session_id: str) -> list[Dict[str, str]]:
        await self.connect()
        key = f"session:{session_id}:history"
        items = await self.client.lrange(key, 0, -1)  # type: ignore[misc]
        return [json.loads(item) for item in items]

    # --- Pipeline progress helpers (FIX 1 / C1+C2) ---

    async def set_pipeline_progress(self, session_id: str, step: str, ttl_seconds: int = 3600):
        """Set the current pipeline step for a session (used by PipelineStrip polling)."""
        await self.connect()
        await self.client.set(f"pipeline_progress:{session_id}", step, ex=ttl_seconds)

    async def get_pipeline_progress(self, session_id: str) -> Optional[str]:
        """Get the current pipeline step for a session."""
        await self.connect()
        return await self.client.get(f"pipeline_progress:{session_id}")

    async def clear_pipeline_progress(self, session_id: str):
        """Clear pipeline progress key after completion or failure."""
        await self.connect()
        await self.client.delete(f"pipeline_progress:{session_id}")

    # --- JTI blacklist helpers (FIX 1 / auth token revocation) ---

    async def blacklist_jti(self, jti: str, expiry_seconds: int):
        """Add a JWT token ID to the blacklist so it can't be reused."""
        await self.connect()
        await self.client.set(f"blacklist:jti:{jti}", "true", ex=expiry_seconds)

    async def is_jti_blacklisted(self, jti: str) -> bool:
        """Check whether a JWT token ID has been revoked."""
        await self.connect()
        result = await self.client.get(f"blacklist:jti:{jti}")
        return result is not None

    # --- User session index helpers (FIX 2 / C3 / M2) ---

    async def add_user_session(self, user_id: str, session_id: str, ttl_seconds: int = 86400):
        """Track a session under a user (sorted set with timestamp score for recency)."""
        await self.connect()
        key = f"user_sessions:{user_id}"
        await self.client.zadd(key, {session_id: time.time()})
        await self.client.expire(key, ttl_seconds)

    async def get_user_sessions(self, user_id: str, with_scores: bool = True) -> Any:
        """Return session IDs for a user, most recent first. With scores if requested."""
        await self.connect()
        key = f"user_sessions:{user_id}"
        if with_scores:
            # M2: Fetch with scores to allow sidebar timestamp bucketing
            results = await self.client.zrevrange(key, 0, -1, withscores=True)
            formatted = []
            for item in results:
                if isinstance(item, (tuple, list)):
                    sid, score = item
                else:
                    sid, score = item, time.time()
                sid_str = sid.decode("utf-8") if isinstance(sid, bytes) else str(sid)
                formatted.append({"id": sid_str, "timestamp": float(score)})
            return formatted
        results = await self.client.zrevrange(key, 0, -1)
        return [s.decode("utf-8") if isinstance(s, bytes) else str(s) for s in results]

    # --- Uploaded context helpers (FIX 13 / C3 / M4) ---

    async def save_uploaded_context(self, session_id: str, file_id: str, text: str, ttl_seconds: int = 86400):
        """Store uploaded file text associated with a session."""
        await self.connect()
        key = f"uploaded_context:{session_id}:{file_id}"
        await self.client.set(key, text, ex=ttl_seconds)
        await self.client.sadd(f"session_uploads:{session_id}", file_id)  # type: ignore[misc]
        await self.client.expire(f"session_uploads:{session_id}", ttl_seconds)

    async def get_uploaded_context(self, session_id: str, file_id: str) -> Optional[str]:
        """Retrieve uploaded file text for a session."""
        await self.connect()
        raw = await self.client.get(f"uploaded_context:{session_id}:{file_id}")
        return raw.decode("utf-8") if isinstance(raw, bytes) else raw

    async def list_uploaded_context_ids(self, session_id: str) -> List[str]:
        """C3: Retrieve all uploaded file IDs for a session."""
        await self.connect()
        members = await self.client.smembers(f"session_uploads:{session_id}")  # type: ignore[misc]
        return [m.decode("utf-8") if isinstance(m, bytes) else str(m) for m in members]

    # --- Background Job Status Helpers (C5) ---

    async def save_job_status(self, job_id: str, data: Dict[str, Any], ttl_seconds: int = 86400):
        """C5: Store background scrape job status under dedicated key namespace."""
        await self.connect()
        key = f"job:{job_id}:status"
        await self.client.set(key, json.dumps(data), ex=ttl_seconds)

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """C5: Retrieve background scrape job status from dedicated key namespace."""
        await self.connect()
        key = f"job:{job_id}:status"
        raw = await self.client.get(key)
        if not raw:
            return None
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        return json.loads(text)

    async def delete_session(self, session_id: str):
        """Clean up all Redis keys associated with a session."""
        await self.connect()
        uploaded_ids = await self.list_uploaded_context_ids(session_id)
        keys_to_delete = [
            f"session:{session_id}:data",
            f"session:{session_id}:owner",
            f"session:{session_id}:history",
            f"pipeline_progress:{session_id}",
            f"session_uploads:{session_id}",
        ]
        for fid in uploaded_ids:
            keys_to_delete.append(f"uploaded_context:{session_id}:{fid}")
        
        owner_id = await self.get_session_owner(session_id)
        if owner_id:
            await self.client.zrem(f"user_sessions:{owner_id}", session_id)

        if keys_to_delete:
            await self.client.delete(*keys_to_delete)

redis_store = RedisStore()

