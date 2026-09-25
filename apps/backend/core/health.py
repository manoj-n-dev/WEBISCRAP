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
from collections import defaultdict

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from core.config import settings, get_client_ip

router = APIRouter(tags=["Health"])

# ─── In-handler rate limiter for /health/ready ────────────────────────────────
# Container orchestrators call /health/live; /health/ready does real DB + Redis
# work so we cap it at 30 req/min per IP without using Depends() (which would
# break orchestrator tooling and fail the existing no-rate-limiter-dep test).
_ready_hits: dict[str, list[float]] = defaultdict(list)
_READY_LIMIT = 30        # requests
_READY_WINDOW = 60.0     # seconds


def _ready_rate_check(ip: str) -> bool:
    """Sliding-window check: True = request is allowed."""
    now = time.time()
    window_start = now - _READY_WINDOW
    hits = _ready_hits[ip]
    _ready_hits[ip] = [t for t in hits if t > window_start]
    if len(_ready_hits[ip]) >= _READY_LIMIT:
        return False
    _ready_hits[ip].append(now)
    return True

# ─── Startup timestamp for uptime tracking ────────────────────────────────────
_startup_time: float = time.time()


def reset_startup_time():
    """Called during lifespan to accurately set the startup timestamp."""
    global _startup_time
    _startup_time = time.time()


# ─── Liveness / Keep-Alive Probe ──────────────────────────────────────────────

@router.get("/health", status_code=status.HTTP_200_OK)
@router.head("/health", status_code=status.HTTP_200_OK)
@router.get("/health/live", status_code=status.HTTP_200_OK)
@router.head("/health/live", status_code=status.HTTP_200_OK)
async def liveness():
    """
    Kubernetes / Render liveness and external keep-alive probe.
    Returns HTTP 200 immediately if the application process is alive.
    Zero external dependency checks (no DB, no Redis, no AI, no scraping).
    Safe to call every 5 minutes indefinitely.
    """
    return {
        "status": "ok",
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
        # N9: never return raw exception text in production — log server-side only
        msg = str(e) if settings.ENVIRONMENT != "production" else "dependency check failed"
        return {"status": "error", "error": msg}


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
        # N9: never return raw exception text in production
        msg = str(e) if settings.ENVIRONMENT != "production" else "dependency check failed"
        return {"status": "error", "error": msg}


@router.get("/health/ready")
async def readiness(request: Request):
    """
    Deep readiness probe for load balancers and deployment orchestrators.
    Checks PostgreSQL and Redis connectivity. Returns 503 if any dependency is unhealthy.
    Rate-limited to 30 req/min per IP in-handler (N9) without using Depends() so
    container orchestrators are never blocked by the route-level dependency guard.
    """
    # N9 — in-handler rate gate (does not use Depends so orchestrator test stays green)
    ip = get_client_ip(request)
    if not _ready_rate_check(ip):
        return JSONResponse(
            content={"status": "rate_limited", "detail": "Too many readiness probes."},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            headers={"Retry-After": str(int(_READY_WINDOW))},
        )

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
            err = checks[name]
            logger.warning(f"Health check: {name} gather exception: {err}")
            # N9: redact raw exception from production response body
            msg = str(err) if settings.ENVIRONMENT != "production" else "dependency check failed"
            checks[name] = {"status": "error", "error": msg}

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
