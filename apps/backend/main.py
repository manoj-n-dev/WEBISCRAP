from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from core.config import settings
from api import api_router
from api.auth import router as auth_router
from api.chat import router as chat_router
from api.scrape import router as scrape_router
from api.export import router as export_router
from api.upload import router as upload_router

# Configure loguru
logger.remove()
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting WEBISCRAP API...")
    yield
    logger.info("Shutting down WEBISCRAP API...")

app = FastAPI(
    title="WEBISCRAP API",
    description="AI-Powered Multi-Agent Intelligent Web Data Extraction Platform",
    version="1.0.0",
    lifespan=lifespan,
)

import time
from fastapi import Request
from core.rate_limit import rate_limiter
from fastapi import Depends

@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    client_ip = request.client.host if request.client else "unknown"
    logger.info(
        f"AUDIT | IP: {client_ip} | "
        f"{request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Time: {process_time:.3f}s"
    )
    return response

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL] if settings.ENVIRONMENT == "production" else ["*", settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"], dependencies=[Depends(rate_limiter)])
app.include_router(scrape_router, prefix="/api/scrape", tags=["Scrape"], dependencies=[Depends(rate_limiter)])
app.include_router(export_router, prefix="/api/export", tags=["Export"])
app.include_router(upload_router, prefix="/api/upload", tags=["Upload"])



@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
