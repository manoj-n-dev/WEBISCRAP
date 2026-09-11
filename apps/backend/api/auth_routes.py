from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from typing import Any
import re

from database.connection import get_session
from models.user import User, UserCreate, UserRead
from auth.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_refresh_token, create_reset_token, decode_reset_token
from auth.email_service import send_password_reset_email
from auth.dependencies import get_current_user
from pydantic import BaseModel
from memory.session_store import redis_store
from core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Generate a password reset token and send reset email.
    Always returns uniform message to prevent email enumeration.
    """
    statement = select(User).where(User.email == request.email)
    result = await db.exec(statement)
    user = result.first()
    
    reset_url = None
    if user and user.is_active and user.email:
        token = create_reset_token(user.id)
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        await send_password_reset_email(user.email, reset_url)
        logger.info(f"Password reset initiated for {user.email}")
    
    response_payload = {"message": "If that email is in our system, we have sent a reset link."}
    if settings.ENVIRONMENT != "production" and reset_url:
        response_payload["dev_reset_url"] = reset_url
        
    return response_payload

@router.post("/reset-password")
async def reset_password(
    req: ResetPasswordRequest,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Verify reset token, validate new password strength, ensure it does NOT match
    the user's old password, update database, and blacklist the reset token.
    """
    payload = decode_reset_token(req.token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
    jti = payload.get("jti")
    if jti and await redis_store.is_jti_blacklisted(jti):
        raise HTTPException(status_code=400, detail="Reset token has already been used")
        
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid reset token payload")
        
    statement = select(User).where(User.id == user_id)
    result = await db.exec(statement)
    user = result.first()
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found or inactive")
        
    # 1. Enforce password strength
    validate_password(req.new_password)
    
    # 2. Verify new password is NOT identical to current/old password
    if user.hashed_password and verify_password(req.new_password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="New password cannot be the same as your old password."
        )
        
    # 3. Update hashed password
    user.hashed_password = get_password_hash(req.new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # 4. Blacklist the reset token so it cannot be used again
    if jti:
        await redis_store.blacklist_jti(jti, settings.RESET_TOKEN_EXPIRE_MINUTES * 60)
        
    logger.info(f"Password reset successfully completed for user {user.email}")
    return {"message": "Password updated successfully. You can now log in with your new password."}


class RefreshTokenRequest(BaseModel):
    refresh_token: str | None = None

def set_refresh_cookie(response: Response, token: str, remember_me: bool = True):
    # M3: Conditionally set max_age; omit for session-only cookie when remember_me is False
    max_age = (settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60) if remember_me else None
    response.set_cookie(
        key="refresh_token",
        value=token,
        max_age=max_age,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
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
        is_blacklisted = await redis_store.is_jti_blacklisted(jti)
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
        
    # FIX 6: Blacklist the old refresh token upon rotation
    if jti:
        expiry_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        await redis_store.blacklist_jti(jti, expiry_seconds)
        
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
            
    user = User.model_validate(user_in, update={"hashed_password": get_password_hash(user_in.password or "")})
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

@router.post("/login")
async def login_access_token(
    response: Response,
    remember_me: bool = Query(default=True),
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
    # M3: Pass remember_me to determine session vs persistent refresh cookie
    set_refresh_cookie(response, new_refresh, remember_me=remember_me)
    
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
            jti = str(payload.get("jti"))
            # Store JTI in Redis with an expiry matching the refresh token lifetime
            expiry_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
            await redis_store.blacklist_jti(jti, expiry_seconds)
            
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}

@router.post("/guest")
async def create_guest_user(
    response: Response,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Create a guest user session.
    """
    user = User(is_guest=True, is_active=True)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    new_refresh = create_refresh_token(user.id)
    set_refresh_cookie(response, new_refresh)
    
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
