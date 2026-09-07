import json
import redis.asyncio as redis
from typing import Dict, Any, Optional, List
from core.config import settings
from loguru import logger
import time

class RedisStore:
    def __init__(self):
        self.redis_client = None

    async def connect(self):
        if self.redis_client is None:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            logger.info("Connected to Redis.")

    async def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        await self.connect()
        data = await self.redis_client.get(f"session:{session_id}:data")
        if data:
            return json.loads(data)
        return None

    async def save_session_data(self, session_id: str, data: Dict[str, Any], ttl_seconds: int = 86400):
        await self.connect()
        await self.redis_client.setex(
            f"session:{session_id}:data",
            ttl_seconds,
            json.dumps(data)
        )
        logger.info(f"[{session_id}] Session data saved to Redis with {ttl_seconds}s TTL.")

    async def set_session_owner(self, session_id: str, owner_id: str, ttl_seconds: int = 86400):
        await self.connect()
        await self.redis_client.setex(
            f"session:{session_id}:owner",
            ttl_seconds,
            owner_id
        )

    async def get_session_owner(self, session_id: str) -> Optional[str]:
        await self.connect()
        return await self.redis_client.get(f"session:{session_id}:owner")

    async def append_conversation_history(self, session_id: str, message: Dict[str, str]):
        await self.connect()
        key = f"session:{session_id}:history"
        await self.redis_client.rpush(key, json.dumps(message))
        await self.redis_client.expire(key, 86400) # Keep history for 1 day

    async def get_conversation_history(self, session_id: str) -> list[Dict[str, str]]:
        await self.connect()
        key = f"session:{session_id}:history"
        items = await self.redis_client.lrange(key, 0, -1)
        return [json.loads(item) for item in items]

    # --- Pipeline progress helpers (FIX 1 / C1+C2) ---

    async def set_pipeline_progress(self, session_id: str, step: str, ttl_seconds: int = 3600):
        """Set the current pipeline step for a session (used by PipelineStrip polling)."""
        await self.connect()
        await self.redis_client.setex(f"pipeline_progress:{session_id}", ttl_seconds, step)

    async def get_pipeline_progress(self, session_id: str) -> Optional[str]:
        """Get the current pipeline step for a session."""
        await self.connect()
        return await self.redis_client.get(f"pipeline_progress:{session_id}")

    async def clear_pipeline_progress(self, session_id: str):
        """Clear pipeline progress key after completion or failure."""
        await self.connect()
        await self.redis_client.delete(f"pipeline_progress:{session_id}")

    # --- JTI blacklist helpers (FIX 1 / auth token revocation) ---

    async def blacklist_jti(self, jti: str, expiry_seconds: int):
        """Add a JWT token ID to the blacklist so it can't be reused."""
        await self.connect()
        await self.redis_client.setex(f"blacklist:jti:{jti}", expiry_seconds, "true")

    async def is_jti_blacklisted(self, jti: str) -> bool:
        """Check whether a JWT token ID has been revoked."""
        await self.connect()
        result = await self.redis_client.get(f"blacklist:jti:{jti}")
        return result is not None

    # --- User session index helpers (FIX 2 / C3) ---

    async def add_user_session(self, user_id: str, session_id: str, ttl_seconds: int = 86400):
        """Track a session under a user (sorted set with timestamp score for recency)."""
        await self.connect()
        key = f"user_sessions:{user_id}"
        await self.redis_client.zadd(key, {session_id: time.time()})
        await self.redis_client.expire(key, ttl_seconds)

    async def get_user_sessions(self, user_id: str) -> List[str]:
        """Return session IDs for a user, most recent first."""
        await self.connect()
        key = f"user_sessions:{user_id}"
        # ZREVRANGEBYSCORE returns highest-score (most recent) first
        return await self.redis_client.zrevrange(key, 0, -1)

    # --- Uploaded context helpers (FIX 13 / M4) ---

    async def save_uploaded_context(self, session_id: str, file_id: str, text: str, ttl_seconds: int = 86400):
        """Store uploaded file text associated with a session."""
        await self.connect()
        key = f"uploaded_context:{session_id}:{file_id}"
        await self.redis_client.setex(key, ttl_seconds, text)
        await self.redis_client.sadd(f"session_uploads:{session_id}", file_id)
        await self.redis_client.expire(f"session_uploads:{session_id}", ttl_seconds)

    async def get_uploaded_context(self, session_id: str, file_id: str) -> Optional[str]:
        """Retrieve uploaded file text for a session."""
        await self.connect()
        return await self.redis_client.get(f"uploaded_context:{session_id}:{file_id}")

redis_store = RedisStore()

