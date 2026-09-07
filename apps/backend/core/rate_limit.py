from fastapi import Request, HTTPException
from core.config import settings, get_client_ip
from memory.session_store import redis_store
import time

async def rate_limiter(request: Request):
    """
    A simple Redis-based sliding window rate limiter.
    Limits requests to RATE_LIMIT_PER_MINUTE per IP address.
    Fails open on transient Redis network/socket errors.
    """
    client_ip = get_client_ip(request)
    key = f"rate_limit:{client_ip}"
    
    try:
        await redis_store.connect()
        redis_client = redis_store.client
        
        # Get current timestamp in seconds
        now = int(time.time())
        window_start = now - 60
        
        # Use a pipeline for atomic operations
        pipeline = redis_client.pipeline()
        
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
    except HTTPException:
        raise
    except Exception as e:
        from loguru import logger
        logger.warning(f"Rate limiter Redis exception (failing open): {e}")
