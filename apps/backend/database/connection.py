"""
I3: Production Database Connection Pooling & Retry
===================================================
Production-grade async database engine with:
- Configurable connection pool sizing (min/max/overflow)
- Connection health validation (pool_pre_ping)
- Connection recycling to handle Neon PostgreSQL idle timeouts
- Graceful startup retry with exponential backoff
- Pool event instrumentation for monitoring
- Separate pool settings for development vs production
"""

import asyncio
from typing import AsyncGenerator

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy import event, text
from loguru import logger

from core.config import settings

# ─── Pool Configuration ──────────────────────────────────────────────────────

_is_production = settings.ENVIRONMENT.lower() == "production"

# Production pool: larger pool, conservative recycling for Neon PostgreSQL
# Development pool: smaller pool, verbose logging
_POOL_CONFIG = {
    "pool_pre_ping": True,                   # Validate connections before use
    "pool_recycle": 270 if _is_production else 300,   # Recycle before Neon's 5 min idle timeout
    "pool_size": 10 if _is_production else 3,         # Steady-state connections
    "max_overflow": 20 if _is_production else 5,      # Burst connections beyond pool_size
    "pool_timeout": 30,                       # Wait up to 30s for a connection from pool
    "echo": False if _is_production else True,         # SQL echo in dev only
    "echo_pool": "debug" if not _is_production else False,  # Pool lifecycle in dev
    "future": True,
}


def _create_engine() -> AsyncEngine:
    """Create the SQLAlchemy async engine with production-tuned pool settings."""
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured.")

    db_url = settings.DATABASE_URL

    engine = create_async_engine(db_url, **_POOL_CONFIG)

    # ─── Pool Event Instrumentation ───────────────────────────────────
    @event.listens_for(engine.sync_engine, "checkout")
    def on_checkout(dbapi_conn, connection_rec, connection_proxy):
        logger.debug(f"DB pool: connection checked out (rec={id(connection_rec)})")

    @event.listens_for(engine.sync_engine, "checkin")
    def on_checkin(dbapi_conn, connection_rec):
        logger.debug(f"DB pool: connection returned (rec={id(connection_rec)})")

    @event.listens_for(engine.sync_engine, "invalidate")
    def on_invalidate(dbapi_conn, connection_rec, exception):
        logger.warning(
            f"DB pool: connection invalidated (rec={id(connection_rec)}, "
            f"reason={exception})"
        )

    return engine


# ─── Engine & Session Factory ─────────────────────────────────────────────────

engine = _create_engine()

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for async database sessions.
    Provides session context, rolls back on unhandled exception, and returns connection to pool.
    """
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


# ─── Startup Connectivity Check with Retry ────────────────────────────────────

async def verify_database_connectivity(max_retries: int = 5, base_delay: float = 1.0):
    """
    Called during application lifespan startup.
    Attempts a lightweight SELECT 1 with exponential backoff.
    Ensures the DB is reachable before accepting traffic.
    """
    for attempt in range(1, max_retries + 1):
        try:
            async with engine.connect() as conn:
                result = await asyncio.wait_for(
                    conn.execute(text("SELECT 1")),
                    timeout=10.0,
                )
                scalar = result.scalar()
                logger.info(
                    f"Database connectivity verified on attempt {attempt} "
                    f"(result={scalar}, pool_size={_POOL_CONFIG['pool_size']}, "
                    f"max_overflow={_POOL_CONFIG['max_overflow']})"
                )
                return True
        except Exception as e:
            delay = base_delay * (2 ** (attempt - 1))  # 1s, 2s, 4s, 8s, 16s
            logger.warning(
                f"Database connection attempt {attempt}/{max_retries} failed: {e}. "
                f"Retrying in {delay:.1f}s..."
            )
            if attempt < max_retries:
                await asyncio.sleep(delay)

    logger.error(
        f"Database connectivity check FAILED after {max_retries} attempts. "
        f"The application may be in a degraded state."
    )
    return False


# ─── Graceful Shutdown ────────────────────────────────────────────────────────

async def dispose_engine():
    """Dispose of the engine pool during application shutdown."""
    logger.info("Disposing database engine and connection pool...")
    await engine.dispose()
    logger.info("Database engine disposed.")
