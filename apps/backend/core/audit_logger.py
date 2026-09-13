"""
I2: Production Audit Logger
============================
Structured, JSON-formatted audit logging with contextual tracing for production.

Features:
- Structured JSON output for log aggregation (ELK, Datadog, CloudWatch)
- Request-scoped correlation IDs (X-Request-ID / auto-generated)
- Separate audit trail for sensitive operations (auth, scrape, export, admin)
- Configurable log levels per environment
- Sanitized output: never logs passwords, tokens, or secrets
"""

import sys
import time
import uuid
from contextvars import ContextVar
from typing import Optional, Any

from loguru import logger as _loguru_logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.config import settings, get_client_ip

# ─── Request-scoped correlation ID ───────────────────────────────────────────
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> Optional[str]:
    """Return the current request correlation ID (available inside request context)."""
    return request_id_ctx.get()


# ─── Sensitive Field Sanitizer ────────────────────────────────────────────────
_SENSITIVE_FIELDS = frozenset({
    "password", "new_password", "old_password", "confirm_password",
    "token", "access_token", "refresh_token", "jwt", "bearer",
    "authorization", "api_key", "secret", "smtp_password",
    "private_key", "firebase_private_key", "otp", "code",
})


def sanitize_dict(data: Any) -> Any:
    """Replace values of sensitive keys with '***REDACTED***'."""
    if not isinstance(data, dict):
        return data
    sanitized = {}
    for key, value in data.items():
        if isinstance(key, str) and key.lower() in _SENSITIVE_FIELDS:
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        else:
            sanitized[key] = value
    return sanitized


# Configure default patcher immediately on import so unconfigured loggers never raise KeyError
_loguru_logger.configure(patcher=lambda record: record["extra"].setdefault("request_id", get_request_id() or "-"))


def _dev_formatter(record: Any) -> str:
    """Format log record with safe fallback for request_id."""
    rid = record["extra"].get("request_id") or get_request_id() or "-"
    record["extra"]["request_id"] = rid
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "[{extra[request_id]}] - <level>{message}</level>\n{exception}"
    )


def _prod_formatter(record: Any) -> str:
    """Format log record as JSON-compatible structured log line."""
    rid = record["extra"].get("request_id") or get_request_id() or "-"
    record["extra"]["request_id"] = rid
    return (
        '{{"timestamp":"{time:YYYY-MM-DDTHH:mm:ss.SSSZ}",'
        '"level":"{level}",'
        '"logger":"{name}",'
        '"function":"{function}",'
        '"line":{line},'
        '"request_id":"{extra[request_id]}",'
        '"message":"{message}"}}\n'
    )


# ─── Structured Logger Configuration ─────────────────────────────────────────

def configure_logging():
    """
    Configure loguru for production-grade structured logging.
    
    - Development: Colorized, human-readable format with DEBUG level
    - Production:  Structured JSON-like format with INFO level, no color codes
    """
    _loguru_logger.remove()

    is_prod = settings.ENVIRONMENT.lower() == "production"
    log_level = "INFO" if is_prod else "DEBUG"

    # Always ensure request_id exists in record["extra"]
    _loguru_logger.configure(patcher=lambda record: record["extra"].setdefault("request_id", get_request_id() or "-"))

    if is_prod:
        # Production: structured format for log aggregation
        _loguru_logger.add(
            sys.stdout,
            format=_prod_formatter,
            level=log_level,
            colorize=False,
            backtrace=False,       # Don't leak internal paths in production
            diagnose=False,        # Don't leak local variables in tracebacks
            enqueue=True,          # Thread-safe async-safe logging
        )
    else:
        # Development: rich, colorized human-readable output
        _loguru_logger.add(
            sys.stdout,
            format=_dev_formatter,
            level=log_level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

    return _loguru_logger


# ─── Audit Logger (Specialized) ──────────────────────────────────────────────

class AuditLogger:
    """
    Specialized logger for security-critical operations.
    All audit log entries are prefixed with 'AUDIT |' for easy grep/filter.
    """

    @staticmethod
    def auth_event(event: str, *, user_id: Optional[str] = None, email: Optional[str] = None, ip: Optional[str] = None, **extra):
        """Log an authentication event (login, logout, register, password reset, etc.)."""
        rid = get_request_id() or "-"
        parts = [
            f"AUDIT | AUTH | event={event}",
            f"request_id={rid}",
        ]
        if user_id:
            parts.append(f"user_id={user_id}")
        if email:
            parts.append(f"email={email}")
        if ip:
            parts.append(f"ip={ip}")
        for k, v in extra.items():
            if k.lower() not in _SENSITIVE_FIELDS:
                parts.append(f"{k}={v}")
        _loguru_logger.info(" | ".join(parts))

    @staticmethod
    def data_event(event: str, *, user_id: Optional[str] = None, session_id: Optional[str] = None, **extra):
        """Log a data mutation event (scrape, export, upload, delete)."""
        rid = get_request_id() or "-"
        parts = [
            f"AUDIT | DATA | event={event}",
            f"request_id={rid}",
        ]
        if user_id:
            parts.append(f"user_id={user_id}")
        if session_id:
            parts.append(f"session_id={session_id}")
        for k, v in extra.items():
            if k.lower() not in _SENSITIVE_FIELDS:
                parts.append(f"{k}={v}")
        _loguru_logger.info(" | ".join(parts))

    @staticmethod
    def security_event(event: str, *, ip: Optional[str] = None, reason: Optional[str] = None, **extra):
        """Log a security event (rate limit hit, invalid token, suspicious activity)."""
        rid = get_request_id() or "-"
        parts = [
            f"AUDIT | SECURITY | event={event}",
            f"request_id={rid}",
        ]
        if ip:
            parts.append(f"ip={ip}")
        if reason:
            parts.append(f"reason={reason}")
        for k, v in extra.items():
            if k.lower() not in _SENSITIVE_FIELDS:
                parts.append(f"{k}={v}")
        _loguru_logger.warning(" | ".join(parts))


audit_log = AuditLogger()


# ─── Request Tracing Middleware ───────────────────────────────────────────────

class RequestTracingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    1. Assigns/propagates a correlation ID (X-Request-ID header)
    2. Logs structured request/response audit lines
    3. Sets request_id in contextvars for downstream use
    """

    async def dispatch(self, request: Request, call_next):
        # Extract or generate request correlation ID
        req_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:16])
        request_id_ctx.set(req_id)

        client_ip = get_client_ip(request)
        start_time = time.monotonic()

        # Log incoming request (skip health probes to reduce noise)
        path = request.url.path
        is_health = path.startswith("/health")
        
        if not is_health:
            _loguru_logger.bind(request_id=req_id).info(
                f"REQ | {request.method} {path} | ip={client_ip}"
            )

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            elapsed_ms = round((time.monotonic() - start_time) * 1000, 2)
            _loguru_logger.bind(request_id=req_id).error(
                f"ERR | {request.method} {path} | ip={client_ip} | "
                f"elapsed={elapsed_ms}ms | error={type(exc).__name__}: {exc}"
            )
            raise

        elapsed_ms = round((time.monotonic() - start_time) * 1000, 2)

        # Log response (skip health probes)
        if not is_health:
            log_func = _loguru_logger.info if response.status_code < 400 else _loguru_logger.warning
            log_func(
                f"RES | {request.method} {path} | ip={client_ip} | "
                f"status={response.status_code} | elapsed={elapsed_ms}ms",
            )

        # Propagate correlation ID to client
        response.headers["X-Request-ID"] = req_id
        return response
