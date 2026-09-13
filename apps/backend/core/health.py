"""
I1: Production Health Check Module
==================================
Provides /health/live and /health/ready endpoints for container orchestrators.

- /health/live  → Lightweight liveness probe (always 200 if process is alive)
- /health/ready → Deep readiness probe that verifies all dependencies:
    • PostgreSQL connectivity + query execution
    • Redis connectivity + read/write
"""

import time
import asyncio
from typing import Dict, Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from loguru import logger

from core.config import settings

router = APIRouter(tags=["Health"])

# ─── Startup timestamp for uptime tracking ────────────────────────────────────
_startup_time: float = time.time()


def reset_startup_time():
    """Called during lifespan to accurately set the startup timestamp."""
    global _startup_time
    _startup_time = time.time()


# ─── Liveness Probe ──────────────────────────────────────────────────────────

@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness():
    """
    Kubernetes / Render liveness probe.
    Returns 200 if the process is alive. No dependency checks.
    """
    return {
        "status": "alive",
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": round(time.time() - _startup_time, 2),
    }


# ─── Readiness Probe ─────────────────────────────────────────────────────────

async def _check_postgres() -> Dict[str, Any]:
    """Verify PostgreSQL connectivity with a lightweight query."""
    from database.connection import engine
    from sqlalchemy import text

    start = time.monotonic()
    try:
        async with engine.connect() as conn:
            result = await asyncio.wait_for(
                conn.execute(text("SELECT 1")),
                timeout=5.0,
            )
            row = result.scalar()
            latency_ms = round((time.monotonic() - start) * 1000, 2)
            return {
                "status": "ok",
                "latency_ms": latency_ms,
                "result": row,
            }
    except asyncio.TimeoutError:
        return {"status": "timeout", "error": "PostgreSQL query timed out (>5s)"}
    except Exception as e:
        logger.warning(f"Health check: PostgreSQL probe failed: {e}")
        return {"status": "error", "error": str(e)}


async def _check_redis() -> Dict[str, Any]:
    """Verify Redis connectivity with a PING and ephemeral key write/read."""
    from memory.session_store import redis_store

    start = time.monotonic()
    try:
        await redis_store.connect()
        client = redis_store.client

        # PING
        async def _ping() -> bool:
            res = client.ping()
            if isinstance(res, bool):
                return res
            return await res

        pong = await asyncio.wait_for(_ping(), timeout=3.0)
        if not pong:
            return {"status": "error", "error": "PING returned False"}

        # Ephemeral write/read/delete cycle
        test_key = "health:probe:readiness"
        await client.set(test_key, "1", ex=10)
        val = await client.get(test_key)
        await client.delete(test_key)

        latency_ms = round((time.monotonic() - start) * 1000, 2)
        return {
            "status": "ok",
            "latency_ms": latency_ms,
            "ping": True,
            "write_read": val == "1",
        }
    except asyncio.TimeoutError:
        return {"status": "timeout", "error": "Redis PING timed out (>3s)"}
    except Exception as e:
        logger.warning(f"Health check: Redis probe failed: {e}")
        return {"status": "error", "error": str(e)}


@router.get("/health/ready")
async def readiness():
    """
    Deep readiness probe for load balancers and deployment orchestrators.
    Checks PostgreSQL and Redis connectivity. Returns 503 if any dependency is unhealthy.
    """
    checks: Dict[str, Any] = {}

    # Run probes concurrently with bounded timeout
    pg_task = asyncio.create_task(_check_postgres())
    redis_task = asyncio.create_task(_check_redis())

    checks["postgres"], checks["redis"] = await asyncio.gather(
        pg_task, redis_task, return_exceptions=True
    )

    # Handle exceptions from gather
    for name in ("postgres", "redis"):
        if isinstance(checks[name], Exception):
            checks[name] = {"status": "error", "error": str(checks[name])}

    all_ok = all(
        isinstance(c, dict) and c.get("status") == "ok"
        for c in checks.values()
    )

    payload = {
        "status": "ready" if all_ok else "degraded",
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": round(time.time() - _startup_time, 2),
        "checks": checks,
    }

    if all_ok:
        return JSONResponse(content=payload, status_code=status.HTTP_200_OK)
    else:
        logger.warning(f"Readiness probe DEGRADED: {checks}")
        return JSONResponse(
            content=payload,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
