import base64
import json
import asyncio
import zlib
import redis.asyncio as redis
from typing import Dict, Any, Optional, List, Union
from core.config import settings
from loguru import logger
import time

_ZPREFIX = "z1:"                 # marks gzip+base64 payloads (older plain-JSON values still load)
_MAX_PAYLOAD_BYTES = 900_000     # Upstash free/PAYG reject single requests > 1 MB

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

    @staticmethod
    def _pack(data: Any) -> str:
        raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        return _ZPREFIX + base64.b64encode(zlib.compress(raw, 6)).decode("ascii")

    @staticmethod
    def _unpack(value: str) -> Any:
        if value.startswith(_ZPREFIX):
            return json.loads(zlib.decompress(base64.b64decode(value[len(_ZPREFIX):])).decode("utf-8"))
        return json.loads(value)

    async def get_session_data(self, session_id: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
        await self.connect()
        data = await self.client.get(f"session:{session_id}:data")
        if data:
            return self._unpack(data)
        return None

    async def save_session_data(self, session_id: str, data: Union[Dict[str, Any], List[Any]], ttl_seconds: int = 1209600):
        """Persist the dataset compressed. If it still exceeds the provider's request limit, rows are trimmed
        (and `truncated` / `total_rows` are recorded) instead of failing silently."""
        await self.connect()
        payload = self._pack(data)
        if len(payload) > _MAX_PAYLOAD_BYTES and isinstance(data, dict) and isinstance(data.get("cleaned_data"), list):
            rows = data["cleaned_data"]
            total = len(rows)
            keep = max(1, int(total * (_MAX_PAYLOAD_BYTES / len(payload)) * 0.9))
            data = {**data, "cleaned_data": rows[:keep], "truncated": True, "total_rows": total}
            payload = self._pack(data)
            logger.warning(f"[{session_id}] Dataset trimmed from {total} to {keep} rows to fit Redis request limit.")
        await self.client.set(f"session:{session_id}:data", payload, ex=ttl_seconds)
        logger.info(f"[{session_id}] Session data saved to Redis ({len(payload)} bytes, {ttl_seconds}s TTL).")

    # --- Ownership / session index / titles ---------------------------------

    async def claim_session(self, session_id: str, owner_id: str, ttl_seconds: int = 1209600) -> bool:
        """Atomically claim an unowned session id (client-generated UUIDs). True if now owned by owner_id."""
        await self.connect()
        created = await self.client.set(f"session:{session_id}:owner", owner_id, ex=ttl_seconds, nx=True)
        if created:
            return True
        return (await self.client.get(f"session:{session_id}:owner")) == owner_id

    async def set_session_title_if_missing(self, session_id: str, title: str, ttl_seconds: int = 1209600):
        await self.connect()
        clean = " ".join((title or "").split())[:60] or "New extraction"
        await self.client.set(f"session:{session_id}:title", clean, ex=ttl_seconds, nx=True)

    async def set_session_title(self, session_id: str, title: str, ttl_seconds: int = 1209600):
        """Unconditionally update the session title (e.g. user rename)."""
        await self.connect()
        clean = " ".join((title or "").split())[:80] or "New extraction"
        await self.client.set(f"session:{session_id}:title", clean, ex=ttl_seconds)

    async def save_uploaded_rows(self, session_id: str, file_id: str, rows: List[Dict[str, Any]], ttl_seconds: int = 1209600):
        """Exact rows of an uploaded CSV/XLSX (used directly as the dataset - no LLM round-trip)."""
        await self.connect()
        await self.client.set(f"uploaded_rows:{session_id}:{file_id}", self._pack(rows), ex=ttl_seconds)

    async def get_uploaded_rows(self, session_id: str, file_id: str) -> Optional[List[Dict[str, Any]]]:
        await self.connect()
        raw = await self.client.get(f"uploaded_rows:{session_id}:{file_id}")
        return self._unpack(raw) if raw else None

    async def save_upload_meta(self, session_id: str, file_id: str, meta: Dict[str, Any], ttl_seconds: int = 1209600):
        await self.connect()
        await self.client.set(f"uploaded_meta:{session_id}:{file_id}", json.dumps(meta), ex=ttl_seconds)

    async def set_session_owner(self, session_id: str, owner_id: str, ttl_seconds: int = 1209600):
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
        await self.client.expire(key, 1209600) # Keep history for 14 days

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

    async def add_user_session(self, user_id: str, session_id: str, ttl_seconds: int = 1209600):
        """Track a session under a user (sorted set with timestamp score for recency)."""
        await self.connect()
        key = f"user_sessions:{user_id}"
        await self.client.zadd(key, {session_id: time.time()})
        await self.client.expire(key, ttl_seconds)
        await self.client.set(f"session:{session_id}:owner", user_id, ex=ttl_seconds, nx=True)

    async def get_user_sessions(self, user_id: str, with_scores: bool = True) -> Any:
        """Most-recent-first list of {id, timestamp, title}. Expired sessions are pruned from the index."""
        await self.connect()
        key = f"user_sessions:{user_id}"
        results = await self.client.zrevrange(key, 0, -1, withscores=True)
        ids = [(sid.decode("utf-8") if isinstance(sid, bytes) else str(sid), float(score)) for sid, score in results]
        if not ids:
            return []
        owners = await self.client.mget([f"session:{sid}:owner" for sid, _ in ids])
        titles = await self.client.mget([f"session:{sid}:title" for sid, _ in ids])
        formatted, stale = [], []
        for (sid, score), owner, title in zip(ids, owners, titles):
            if owner != user_id:
                stale.append(sid)
                continue
            formatted.append({"id": sid, "timestamp": score, "title": title or "New extraction"})
        if stale:
            await self.client.zrem(key, *stale)
        if not with_scores:
            return [s["id"] for s in formatted]
        return formatted

    # --- Uploaded context helpers (FIX 13 / C3 / M4) ---

    async def save_uploaded_context(self, session_id: str, file_id: str, text: str, ttl_seconds: int = 1209600):
        """Store uploaded file text associated with a session."""
        await self.connect()
        key = f"uploaded_context:{session_id}:{file_id}"
        await self.client.set(key, text[: settings.MAX_UPLOAD_TEXT_CHARS], ex=ttl_seconds)
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

    # --- Background Job Status & Durable Queue Helpers (H-05 / C5) ---

    async def save_job_status(self, job_id: str, data: Dict[str, Any], ttl_seconds: int = 86400):
        """Store background scrape job status under dedicated key namespace."""
        await self.connect()
        key = f"job:{job_id}:status"
        await self.client.set(key, json.dumps(data), ex=ttl_seconds)

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve background scrape job status from dedicated key namespace."""
        await self.connect()
        key = f"job:{job_id}:status"
        raw = await self.client.get(key)
        if not raw:
            return None
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        return json.loads(text)

    async def enqueue_scrape_job(self, job_data: Dict[str, Any]) -> str:
        """
        H-05: Push a durable scrape job into the Redis queue.
        Persists across server restarts and container recycling.
        """
        await self.connect()
        job_id = job_data["job_id"]
        queue_key = "queue:scrape_jobs"
        await self.save_job_status(job_id, {
            "job_id": job_id,
            "status": "queued",
            "target_url": job_data.get("target_url"),
            "extraction_goal": job_data.get("extraction_goal"),
            "owner_id": job_data.get("owner_id"),
            "created_at": time.time(),
        })
        await self.client.rpush(queue_key, json.dumps(job_data))  # type: ignore[misc]
        return job_id

    async def dequeue_scrape_job(self, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """
        H-05: Atomically pop the next pending scrape job from the Redis queue.
        Uses blpop with a timeout for blocking async polling.
        """
        await self.connect()
        queue_key = "queue:scrape_jobs"
        try:
            res = await self.client.blpop(queue_key, timeout=timeout)  # type: ignore[misc]
            if not res:
                return None
            # res is tuple: (key, value)
            raw_job = res[1]
            text = raw_job.decode("utf-8") if isinstance(raw_job, bytes) else raw_job
            return json.loads(text)
        except Exception as e:
            logger.warning(f"Error popping from scrape job queue: {e}")
            return None

    async def update_job_status(
        self,
        job_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """H-05: Atomically update status and output of a scrape job."""
        current = await self.get_job_status(job_id) or {"job_id": job_id}
        current["status"] = status
        current["updated_at"] = time.time()
        if result is not None:
            current["result"] = result
        if error is not None:
            current["error"] = error
        await self.save_job_status(job_id, current)

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
        keys_to_delete.append(f"session:{session_id}:title")
        for fid in uploaded_ids:
            keys_to_delete.append(f"uploaded_context:{session_id}:{fid}")
            keys_to_delete.append(f"uploaded_rows:{session_id}:{fid}")
            keys_to_delete.append(f"uploaded_meta:{session_id}:{fid}")
        
        owner_id = await self.get_session_owner(session_id)
        if owner_id:
            await self.client.zrem(f"user_sessions:{owner_id}", session_id)

        if keys_to_delete:
            await self.client.delete(*keys_to_delete)

redis_store = RedisStore()

