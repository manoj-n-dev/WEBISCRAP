import sys
import os

# Ensure backend directory is on sys.path so modules resolve whether invoked from root or backend
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import FastAPI, Depends, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# I2: Initialize structured logging BEFORE any other imports that use logger
from core.audit_logger import configure_logging, RequestTracingMiddleware, audit_log

logger = configure_logging()

from core.config import settings, get_client_ip
from core.rate_limit import rate_limiter
from core.health import router as health_router, reset_startup_time
from api.auth_routes import router as auth_router
from api.chat import router as chat_router
from api.scrape import router as scrape_router
from api.export import router as export_router
from api.upload import router as upload_router
from workers.scrape_worker import scrape_worker
from database.connection import verify_database_connectivity, dispose_engine

from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting WEBISCRAP API in {settings.ENVIRONMENT} mode...")

    # I1: Record accurate startup time for health probes
    reset_startup_time()

    # Production security assertions (C-04 / Section 16)
    if settings.ENVIRONMENT == "production":
        if not settings.JWT_SECRET or settings.JWT_SECRET == "dev-secret-key-change-in-production" or len(settings.JWT_SECRET) < 32:
            raise RuntimeError(
                "CRITICAL PRODUCTION ERROR: In production mode, JWT_SECRET must be explicitly set "
                "to a cryptographically secure key of at least 32 characters."
            )
        if not settings.DATABASE_URL:
            raise RuntimeError("CRITICAL PRODUCTION ERROR: DATABASE_URL must be configured.")
        if not settings.REDIS_URL:
            raise RuntimeError("CRITICAL PRODUCTION ERROR: REDIS_URL must be configured.")

    # I3: Verify database connectivity with retry before accepting traffic
    db_ok = await verify_database_connectivity(max_retries=5, base_delay=1.0)
    if not db_ok:
        logger.error("Database is unreachable after retries — API starting in degraded mode")

    # H-05: Start durable Redis scrape queue worker
    await scrape_worker.start()

    audit_log.data_event("app_startup", environment=settings.ENVIRONMENT)

    yield

    # Graceful shutdown sequence
    audit_log.data_event("app_shutdown", environment=settings.ENVIRONMENT)

    # H-05: Gracefully stop scrape worker on shutdown
    await scrape_worker.stop()

    # I3: Dispose database connection pool
    await dispose_engine()

    logger.info("Shutting down WEBISCRAP API...")


app = FastAPI(
    title="WEBISCRAP API",
    description="AI-Powered Multi-Agent Intelligent Web Data Extraction Platform",
    version="1.0.0",
    lifespan=lifespan,
    # I1: Disable docs in production to reduce attack surface
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Section 20: Safe global exception handler prevents leaking stack traces or python internals
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled server exception on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

# I2: Request tracing middleware (correlation IDs + structured request/response logging)
# This REPLACES the previous audit_logging_middleware with a production-grade implementation
app.add_middleware(RequestTracingMiddleware)

# C6 & M6: Never combine "*" with allow_credentials=True.
# Tighten CORS in production to only settings.FRONTEND_URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL] if settings.ENVIRONMENT == "production" else [settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],  # I2: Allow clients to read correlation ID
)

# I1: Health check endpoints (no rate limiting — must always respond for orchestrators)
app.include_router(health_router)

# C5: Single registration point for all routers. No api_router composition.
# M4 & H6: Rate limiter applied to all endpoints (including auth, upload, and export).
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"], dependencies=[Depends(rate_limiter)])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"], dependencies=[Depends(rate_limiter)])
app.include_router(scrape_router, prefix="/api/scrape", tags=["Scrape"], dependencies=[Depends(rate_limiter)])
app.include_router(export_router, prefix="/api/export", tags=["Export"], dependencies=[Depends(rate_limiter)])
app.include_router(upload_router, prefix="/api/upload", tags=["Upload"], dependencies=[Depends(rate_limiter)])


if __name__ == "__main__":
    import os
    import uvicorn

    # Render injects PORT dynamically; fallback to 8000 for local development
    port = int(os.environ.get("PORT", 8000))
    is_dev = settings.ENVIRONMENT.lower() == "development"

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=is_dev)
