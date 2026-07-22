import json
import redis.asyncio as redis
from typing import Dict, Any, Optional
from core.config import settings
from loguru import logger

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

redis_store = RedisStore()
