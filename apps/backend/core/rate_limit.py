import time
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
        error_message: str = "Too Many Requests. Please wait before trying again.",
        skip_suffixes: tuple = (),
    ):
        self.skip_suffixes = skip_suffixes
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
        if self.skip_suffixes and request.url.path.rstrip("/").endswith(self.skip_suffixes):
            return                                    # e.g. the 1-2 s pipeline /progress poll
        identifier = self.key_func(request)
        key = f"{self.prefix}:{identifier}"
        now = time.time()

        try:
            await redis_store.connect()
            client = redis_store.client
            # Fixed window: INCR (+ EXPIRE on first hit). 1-2 Redis commands per request (was 4) and
            # rejected requests no longer extend the block (the old sliding window never drained under polling).
            count = await client.incr(key)
            if count == 1:
                await client.expire(key, self.window_seconds)
            if count > self.limit:
                ttl = await client.ttl(key)
                if ttl is None or ttl < 0:
                    await client.expire(key, self.window_seconds)
                    ttl = self.window_seconds
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=self.error_message,
                    headers={"Retry-After": str(max(1, int(ttl)))},
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Rate limiter Redis error on '{self.prefix}' (activating local memory fallback): {e}")
            if not self._check_in_memory_fallback(key, now):
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=self.error_message)


def user_or_ip_key(request: Request) -> str:
    """Authenticated API calls are limited PER USER (students behind one campus NAT no longer share a bucket);
    anonymous/auth endpoints keep the per-IP key."""
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        try:
            from auth.security import decode_access_token
            payload = decode_access_token(auth[7:].strip())
            if payload and payload.get("sub"):
                return f"u:{payload['sub']}"
        except Exception:
            pass
    return get_client_ip(request)


# General API rate limiter: 60 requests per minute
rate_limiter = RateLimiter(
    limit=settings.RATE_LIMIT_PER_MINUTE,
    window_seconds=60,
    prefix="rate_limit:global",
    key_func=user_or_ip_key,
    skip_suffixes=("/progress",),
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
