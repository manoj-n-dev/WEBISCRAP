# ==============================================================================
# WEBISCRAP — Production Backend Dockerfile
# Optimized for Render Web Services & Worker Deployments
# ==============================================================================

FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies (including tesseract for OCR and certificates)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium into a SHARED path. The default (~/.cache) is /root/.cache when installed as root,
# which the non-root `appuser` cannot read -> Chromium could never launch and every JS page silently fell back to static fetch.
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN python -m playwright install --with-deps chromium && chmod -R a+rX /ms-playwright

# Create a non-privileged application user for security
RUN groupadd -g 10001 appuser && \
    useradd -u 10001 -g appuser -s /bin/bash -m appuser

# Copy application source code
COPY . /app

# Grant appuser ownership of workspace and uploads directory
RUN mkdir -p /app/uploads && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose default backend port
EXPOSE 8000

# Health check using the lightweight /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Default command starts FastAPI production ASGI server with dynamic port binding
# Retry migrations (Neon may still be waking up) before starting the API
CMD ["sh", "-c", "(alembic upgrade head || (sleep 5 && alembic upgrade head) || (sleep 10 && alembic upgrade head)) && exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
