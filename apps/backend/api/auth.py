from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import Any
import re

from database.connection import get_session
from models.user import User, UserCreate, UserRead
from auth.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_refresh_token
from auth.dependencies import get_current_user
from pydantic import BaseModel
from memory.session_store import redis_store
from core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ForgotPasswordRequest(BaseModel):
    email: str

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Mock forgot password endpoint.
    In a real app, this would generate a reset token and send an email.
    """
    statement = select(User).where(User.email == request.email)
    result = await db.exec(statement)
    user = result.first()
    
    if user:
        # Generate token and send email logic goes here
        logger.info(f"Password reset requested for {user.email}")
    
    # Always return success to prevent email enumeration
    return {"message": "If that email is in our system, we have sent a reset link."}

class RefreshTokenRequest(BaseModel):
    refresh_token: str | None = None

def set_refresh_cookie(response: Response, token: str):
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

@router.post("/refresh")
async def refresh_access_token(
    request: Request,
    response: Response,
    body: RefreshTokenRequest | None = None,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Refresh access and refresh tokens using a valid refresh token.
    """
    refresh_token = request.cookies.get("refresh_token") or (body.refresh_token if body else None)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
        
    payload = decode_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    jti = payload.get("jti")
    if jti:
        is_blacklisted = await redis_store.redis.get(f"blacklist:jti:{jti}")
        if is_blacklisted:
            raise HTTPException(status_code=401, detail="Refresh token has been revoked")
            
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    statement = select(User).where(User.id == user_id)
    result = await db.exec(statement)
    user = result.first()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
        
    new_refresh = create_refresh_token(user.id)
    set_refresh_cookie(response, new_refresh)
    
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }

def validate_password(password: str | None) -> None:
    """Enforce password strength requirements."""
    if not password:
        raise HTTPException(status_code=400, detail="Password cannot be empty.")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")
    if not re.search(r'[0-9]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number.")

@router.post("/register", response_model=UserRead)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Register a new user.
    """
    # Validate password strength
    validate_password(user_in.password)
    
    if user_in.email:
        statement = select(User).where(User.email == user_in.email)
        result = await db.exec(statement)
        user = result.first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )
            
    user = User.model_validate(user_in, update={"hashed_password": get_password_hash(user_in.password)})
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login")
async def login_access_token(
    response: Response,
    db: AsyncSession = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    statement = select(User).where(User.email == form_data.username)
    result = await db.exec(statement)
    user = result.first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    if not user.hashed_password or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    new_refresh = create_refresh_token(user.id)
    set_refresh_cookie(response, new_refresh)
    
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }

@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    body: RefreshTokenRequest | None = None,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Logout by invalidating the refresh token.
    """
    refresh_token = request.cookies.get("refresh_token") or (body.refresh_token if body else None)
    if refresh_token:
        payload = decode_refresh_token(refresh_token)
        if payload and payload.get("jti"):
            jti = payload.get("jti")
            # Store JTI in Redis with an expiry matching the refresh token lifetime
            expiry_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
            await redis_store.redis.setex(f"blacklist:jti:{jti}", expiry_seconds, "true")
            
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}

@router.post("/guest")
async def create_guest_user(
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Create a guest user session.
    """
    user = User(is_guest=True, is_active=True)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "user_id": user.id
    }

from auth.providers import verify_google_token, verify_firebase_token

class TokenRequest(BaseModel):
    id_token: str

@router.post("/google")
async def login_google(
    request: TokenRequest,
    response: Response,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Login or register via Google OAuth ID token.
    """
    try:
        idinfo = verify_google_token(request.id_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    email = idinfo.get("email")
    google_id = idinfo.get("sub")
    
    # Try finding by google_id first, then email
    statement = select(User).where((User.google_id == google_id) | (User.email == email))
    result = await db.exec(statement)
    user = result.first()
    
    if not user:
        # Create new user
        user = User(email=email, google_id=google_id, is_active=True)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif not user.google_id:
        # Link google account if they previously signed up with email
        user.google_id = google_id
        db.add(user)
        await db.commit()
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    new_refresh = create_refresh_token(user.id)
    set_refresh_cookie(response, new_refresh)
    
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }

@router.post("/phone")
async def login_phone(
    request: TokenRequest,
    response: Response,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Login or register via Firebase Phone OTP ID token.
    """
    try:
        decoded_token = verify_firebase_token(request.id_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    phone_number = decoded_token.get("phone_number")
    if not phone_number:
        raise HTTPException(status_code=400, detail="Firebase token does not contain a phone number")
        
    statement = select(User).where(User.phone_number == phone_number)
    result = await db.exec(statement)
    user = result.first()
    
    if not user:
        user = User(phone_number=phone_number, is_active=True)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    new_refresh = create_refresh_token(user.id)
    set_refresh_cookie(response, new_refresh)
        
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }
