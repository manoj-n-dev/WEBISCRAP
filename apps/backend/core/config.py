from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os

class Settings(BaseSettings):
    # API Keys (Groq only)
    GROQ_API_KEYS: str

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # JWT
    JWT_SECRET: str
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
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def groq_keys_list(self) -> List[str]:
        return [k.strip() for k in self.GROQ_API_KEYS.split(",") if k.strip()]

settings = Settings()
