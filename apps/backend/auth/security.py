from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
import uuid
from jose import jwt, JWTError
from passlib.context import CryptContext
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(
    subject: Union[str, Any],
    token_version: int = 1,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a signed JWT access token with explicit type='access' and token_version."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "token_version": token_version,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(
    subject: Union[str, Any],
    token_version: int = 1
) -> str:
    """Create a signed JWT refresh token with explicit type='refresh' and token_version."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "token_version": token_version,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """Decode access token with POSITIVE type assertion (type == 'access')."""
    try:
        decoded_token = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if decoded_token.get("type") != "access":
            return None
        return decoded_token
    except JWTError:
        return None

def decode_refresh_token(token: str) -> Optional[dict]:
    """Decode refresh token with POSITIVE type assertion (type == 'refresh')."""
    try:
        decoded_token = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if decoded_token.get("type") != "refresh":
            return None
        return decoded_token
    except JWTError:
        return None

def create_reset_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT password-reset token with explicit type='reset'."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "reset",
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_reset_token(token: str) -> Optional[dict]:
    """Decode reset token with POSITIVE type assertion (type == 'reset')."""
    try:
        decoded_token = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if decoded_token.get("type") != "reset":
            return None
        return decoded_token
    except JWTError:
        return None

def create_verification_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT email verification token with explicit type='verify_email'."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Default 24 hours for email verification links
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "verify_email",
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_verification_token(token: str) -> Optional[dict]:
    """Decode verification token with POSITIVE type assertion (type == 'verify_email')."""
    try:
        decoded_token = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if decoded_token.get("type") != "verify_email":
            return None
        return decoded_token
    except JWTError:
        return None


