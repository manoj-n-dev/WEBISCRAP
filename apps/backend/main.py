import sys
import os
import time

# Ensure backend directory is on sys.path so modules resolve whether invoked from root or backend
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import FastAPI, Depends, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from core.config import settings, get_client_ip
from core.rate_limit import rate_limiter
from api.auth_routes import router as auth_router
from api.chat import router as chat_router
from api.scrape import router as scrape_router
from api.export import router as export_router
from api.upload import router as upload_router
from workers.scrape_worker import scrape_worker

from fastapi.responses import JSONResponse

# Configure loguru
logger.remove()
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting WEBISCRAP API in {settings.ENVIRONMENT} mode...")
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
            
    # H-05: Start durable Redis scrape queue worker
    await scrape_worker.start()
    
    yield
    
    # H-05: Gracefully stop scrape worker on shutdown
    await scrape_worker.stop()
    logger.info("Shutting down WEBISCRAP API...")

app = FastAPI(
    title="WEBISCRAP API",
    description="AI-Powered Multi-Agent Intelligent Web Data Extraction Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Section 20: Safe global exception handler prevents leaking stack traces or python internals
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled server exception on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )


@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    client_ip = get_client_ip(request)
    logger.info(
        f"AUDIT | IP: {client_ip} | "
        f"{request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Time: {process_time:.3f}s"
    )
    return response

# C6 & M6: Never combine "*" with allow_credentials=True.
# Tighten CORS in production to only settings.FRONTEND_URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL] if settings.ENVIRONMENT == "production" else [settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# C5: Single registration point for all routers. No api_router composition.
# M4 & H6: Rate limiter applied to all endpoints (including auth, upload, and export).
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"], dependencies=[Depends(rate_limiter)])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"], dependencies=[Depends(rate_limiter)])
app.include_router(scrape_router, prefix="/api/scrape", tags=["Scrape"], dependencies=[Depends(rate_limiter)])
app.include_router(export_router, prefix="/api/export", tags=["Export"], dependencies=[Depends(rate_limiter)])
app.include_router(upload_router, prefix="/api/upload", tags=["Upload"], dependencies=[Depends(rate_limiter)])


@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
