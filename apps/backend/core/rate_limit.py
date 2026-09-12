import time
import uuid
from typing import Optional, Callable
from collections import defaultdict
from fastapi import Request, HTTPException, status
from core.config import settings, get_client_ip
from memory.session_store import redis_store
from loguru import logger

# Thread-safe in-memory fallback cache for rate-limiting when Redis is unavailable.
# Structure: { key: [timestamp1, timestamp2, ...] }
_in_memory_rate_cache: dict[str, list[float]] = defaultdict(list)

class RateLimiter:
    """
    Production-grade sliding-window rate limiter.
    
    Primary storage: Redis sorted sets.
    Resilience Policy (Section 14 / H-03):
      If Redis encounters network or socket errors, sensitive auth limits DO NOT fail open.
      Instead, they fall back to a process-local sliding window memory cache.
      This ensures brute-force attacks remain actively throttled even during Redis hiccups,
      without crashing or taking down the API.
    """
    def __init__(
        self,
        limit: int,
        window_seconds: int,
        prefix: str = "rate_limit",
        key_func: Optional[Callable[[Request], str]] = None,
        error_message: str = "Too Many Requests. Please wait before trying again."
    ):
        self.limit = limit
        self.window_seconds = window_seconds
        self.prefix = prefix
        self.key_func = key_func or (lambda req: get_client_ip(req))
        self.error_message = error_message

    def _check_in_memory_fallback(self, key: str, now: float) -> bool:
        """Process-local sliding window rate limit fallback."""
        window_start = now - self.window_seconds
        timestamps = _in_memory_rate_cache[key]
        # Prune older timestamps
        _in_memory_rate_cache[key] = [t for t in timestamps if t > window_start]
        if len(_in_memory_rate_cache[key]) >= self.limit:
            return False
        _in_memory_rate_cache[key].append(now)
        return True

    async def __call__(self, request: Request):
        identifier = self.key_func(request)
        key = f"{self.prefix}:{identifier}"
        now = time.time()
        window_start = now - self.window_seconds

        try:
            await redis_store.connect()
            redis_client = redis_store.client

            pipeline = redis_client.pipeline()
            pipeline.zremrangebyscore(key, 0, window_start)
            pipeline.zcard(key)
            unique_member = f"{int(now)}:{uuid.uuid4().hex[:8]}"
            pipeline.zadd(key, {unique_member: now})
            pipeline.expire(key, self.window_seconds)

            results = await pipeline.execute()
            request_count = results[1]

            if request_count >= self.limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=self.error_message
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(
                f"Rate limiter Redis error on '{self.prefix}' (activating local memory fallback): {e}"
            )
            # Use local memory fallback rather than failing completely open
            allowed = self._check_in_memory_fallback(key, now)
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=self.error_message
                )

# General API rate limiter: 60 requests per minute
rate_limiter = RateLimiter(
    limit=settings.RATE_LIMIT_PER_MINUTE,
    window_seconds=60,
    prefix="rate_limit:global"
)

# Dedicated Auth Rate Limiters (Section 13)
login_rate_limiter = RateLimiter(
    limit=5,
    window_seconds=60,
    prefix="rate_limit:login",
    error_message="Too many login attempts. Please wait 1 minute before trying again."
)

registration_rate_limiter = RateLimiter(
    limit=5,
    window_seconds=60,
    prefix="rate_limit:register",
    error_message="Too many registration attempts. Please wait 1 minute before trying again."
)

forgot_password_rate_limiter = RateLimiter(
    limit=3,
    window_seconds=60,
    prefix="rate_limit:forgot_pw",
    error_message="Too many password reset requests. Please wait 1 minute before trying again."
)

resend_verification_rate_limiter = RateLimiter(
    limit=2,
    window_seconds=300, # 2 requests per 5 minutes
    prefix="rate_limit:resend_verify",
    error_message="Too many verification requests. Please wait 5 minutes before trying again."
)

guest_rate_limiter = RateLimiter(
    limit=5,
    window_seconds=60,
    prefix="rate_limit:guest",
    error_message="Too many guest sessions requested. Please wait 1 minute before trying again."
)
