from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from fastapi import Request
import os

# FIX 17: Support .env in PROJECT_ROOT (root), BACKEND_DIR (apps/backend), or current working directory
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, "..", ".."))

class Settings(BaseSettings):
    # API Keys (Groq only)
    GROQ_API_KEYS: str = ""

    # Database
    DATABASE_URL: str = ""

    # Redis
    REDIS_URL: str = ""

    # JWT
    JWT_SECRET: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OAuth (Google) — Optional for dev, required for Google Login
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Firebase — Optional for dev, required for Phone OTP
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_PRIVATE_KEY_ID: str = ""
    FIREBASE_PRIVATE_KEY: str = ""
    FIREBASE_CLIENT_EMAIL: str = ""
    FIREBASE_CLIENT_ID: str = ""
    FIREBASE_CLIENT_X509_CERT_URL: str = ""

    # Environment
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_CORS_ORIGINS: str = ""
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 120

    # SMTP / Email Service
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True
    EMAILS_FROM_EMAIL: str = "noreply@webiscrap.com"
    EMAILS_FROM_NAME: str = "WEBISCRAP"
    RESET_TOKEN_EXPIRE_MINUTES: int = 15

    # ── Groq / LLM budget (NEW) ────────────────────────────────────────────
    # "free" keeps every request under Groq's free-tier 8,000 TPM ceiling. Set to "dev" after upgrading.
    GROQ_TIER: str = "free"
    LLM_MAX_WAIT_SECONDS: int = 15           # absorb short 429 waits server-side instead of failing
    ALLOW_HEURISTIC_FALLBACK: bool = False   # dev-only regex extraction when the LLM is down (never fabricate in prod)
    ANALYZER_MODE: str = "heuristic"         # "heuristic" (no LLM call) | "llm"
    PLANNER_MODE: str = "llm"                # "llm" | "fast" (skip the planner LLM call: ~1-3 s and ~1.5K tokens faster per extraction)
    CLEANER_MODE: str = "deterministic"      # "deterministic" | "llm"

    # ── Data limits (NEW) ──────────────────────────────────────────────────
    MAX_DATASET_ROWS: int = 5000             # rows persisted per session (Upstash free: 1 MB / request)
    CHAT_PREVIEW_ROWS: int = 200             # rows echoed back in a /api/chat response
    MAX_UPLOAD_TEXT_CHARS: int = 200_000     # parsed-file text stored per upload

    # ── Background queue (NEW) ─────────────────────────────────────────────
    MAX_CONCURRENT_BROWSERS: int = 1         # parallel Chromium instances (1 for 512 MB instances)
    ENABLE_SCRAPE_WORKER: bool = False       # polling worker burns Upstash commands; UI does not use it

    # ── Email delivery (NEW) — Render free blocks SMTP ports 25/465/587, use an HTTPS API ──
    EMAIL_PROVIDER: str = "auto"             # auto | brevo | resend | smtp
    BREVO_API_KEY: str = ""
    RESEND_API_KEY: str = ""

    # FIX 15 (M7): Set to True only when behind a trusted reverse proxy (Vercel/Render/Nginx)
    TRUST_PROXY_HEADERS: bool = False
    
    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(PROJECT_ROOT, ".env"),
            os.path.join(BACKEND_DIR, ".env"),
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def groq_is_paid_tier(self) -> bool:
        return self.GROQ_TIER.strip().lower() in ("dev", "developer", "paid", "enterprise")

    @property
    def groq_keys_list(self) -> List[str]:
        return [k.strip() for k in self.GROQ_API_KEYS.split(",") if k.strip()]

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        """
        C-04 Production Secret Fallback Protection:
        Fail fast at startup in production if default/weak secrets are detected or
        critical datastores are not configured.
        """
        if self.ENVIRONMENT.lower() == "production":
            if not self.JWT_SECRET or self.JWT_SECRET == "dev-secret-key-change-in-production" or len(self.JWT_SECRET) < 32:
                raise ValueError("CRITICAL: JWT_SECRET must be configured with a random secure string of at least 32 characters in production.")
            if not self.DATABASE_URL:
                raise ValueError("CRITICAL: DATABASE_URL must be configured in production.")
            if not self.REDIS_URL:
                raise ValueError("CRITICAL: REDIS_URL must be configured in production.")
        return self

settings = Settings()

def get_client_ip(request: Request) -> str:
    """
    FIX 15 (M7) & N5: Extract client IP safely.
    When TRUST_PROXY_HEADERS is enabled, checks CF-Connecting-IP first (from trusted Cloudflare/Render edge),
    or extracts the last IP in X-Forwarded-For (Render appends the real client IP at the end of the chain).
    Otherwise falls back to direct connection host (prevents header spoofing).
    """
    if settings.TRUST_PROXY_HEADERS:
        cf_ip = request.headers.get("CF-Connecting-IP")
        if cf_ip and cf_ip.strip():
            return cf_ip.strip()
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
