from fastapi import Request, HTTPException
from core.config import settings
from memory.session_store import redis_store
import time

async def rate_limiter(request: Request):
    """
    A simple Redis-based sliding window rate limiter.
    Limits requests to RATE_LIMIT_PER_MINUTE per IP address.
    """
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:{client_ip}"
    
    await redis_store.connect()
    redis = redis_store.redis_client
    
    # Get current timestamp in seconds
    now = int(time.time())
    window_start = now - 60
    
    # Use a pipeline for atomic operations
    pipeline = redis.pipeline()
    
    # Remove old requests outside the 1-minute window
    pipeline.zremrangebyscore(key, 0, window_start)
    
    # Count how many requests are in the current window
    pipeline.zcard(key)
    
    import uuid
    # Add the current request
    unique_member = f"{now}:{uuid.uuid4().hex[:8]}"
    pipeline.zadd(key, {unique_member: now})
    
    # Set expiration on the key so it cleans up after a minute of inactivity
    pipeline.expire(key, 60)
    
    results = await pipeline.execute()
    
    # results[1] is the output of zcard
    request_count = results[1]
    
    if request_count >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=429,
            detail="Too Many Requests. Please wait a minute before trying again."
        )
