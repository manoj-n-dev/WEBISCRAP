from fastapi import FastAPI
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

app = FastAPI(
    title="WEBISCRAP API",
    description="AI-Powered Multi-Agent Intelligent Web Data Extraction Platform",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development, should be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(scrape_router, prefix="/api/scrape", tags=["Scrape"])
app.include_router(export_router, prefix="/api/export", tags=["Export"])
app.include_router(upload_router, prefix="/api/upload", tags=["Upload"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting WEBISCRAP API...")

@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
