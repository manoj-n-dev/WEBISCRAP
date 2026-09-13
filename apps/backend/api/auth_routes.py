from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from typing import Any, Optional
import re
import uuid
from loguru import logger

from database.connection import get_session
from models.user import User, UserRegisterRequest, UserRead
from auth.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    create_reset_token,
    decode_reset_token,
    create_verification_token,
    decode_verification_token,
)
from auth.email_service import send_password_reset_email, send_verification_email
from auth.dependencies import get_current_user
from pydantic import BaseModel, EmailStr
from memory.session_store import redis_store
from core.config import settings
from core.rate_limit import (
    login_rate_limiter,
    registration_rate_limiter,
    forgot_password_rate_limiter,
    resend_verification_rate_limiter,
    guest_rate_limiter,
)
from auth.providers import verify_google_token, verify_firebase_token
from core.audit_logger import audit_log, get_request_id

router = APIRouter()

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class TokenRequest(BaseModel):
    id_token: str

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

def set_refresh_cookie(response: Response, token: str, remember_me: bool = True):
    """Set secure HttpOnly cookie for refresh token."""
    max_age = (settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60) if remember_me else None
    is_prod = settings.ENVIRONMENT == "production"
    response.set_cookie(
        key="refresh_token",
        value=token,
        max_age=max_age,
        httponly=True,
        secure=is_prod,
        samesite="none" if is_prod else "lax",
    )

def clear_refresh_cookie(response: Response):
    """Clear the refresh token cookie with matching cross-origin security flags."""
    is_prod = settings.ENVIRONMENT == "production"
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=is_prod,
        samesite="none" if is_prod else "lax",
    )

# --- 1. REGISTRATION WITH STRICT DTO & EMAIL VERIFICATION ---

@router.post("/register", dependencies=[Depends(registration_rate_limiter)])
async def register(
    user_in: UserRegisterRequest,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Register a new user with strict DTO to prevent privilege escalation.
    Creates user with is_verified=False and sends a secure single-use verification token.
    """
    validate_password(user_in.password)
    
    # Check if user already exists
    statement = select(User).where(User.email == user_in.email)
    result = await db.exec(statement)
    existing_user = result.first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system."
        )
        
    # Explicit User model construction: privileged fields are hardcoded to safe defaults
    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        is_verified=False,
        is_superuser=False,
        is_guest=False,
        token_version=1,
    )
    
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system."
        )

    # Generate single-use email verification token
    verify_token = create_verification_token(new_user.id)
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={verify_token}"
    email_res = await send_verification_email(user_in.email, verify_url)

    audit_log.auth_event("register", user_id=str(new_user.id), email=new_user.email or user_in.email)
    
    response_payload = {
        "id": str(new_user.id),
        "email": new_user.email,
        "full_name": new_user.full_name,
        "is_verified": False,
        "message": "Registration successful. Please check your email to verify your account before logging in."
    }
    # Dev/test only helper: never return token or URL in production
    if settings.ENVIRONMENT != "production" and email_res.get("verify_url"):
        response_payload["dev_verify_url"] = email_res.get("verify_url")

    return response_payload

# --- 2. EMAIL VERIFICATION CONFIRMATION & RESEND ---

@router.get("/verify-email")
async def verify_email(
    token: str = Query(..., description="The email verification token"),
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Validate email verification token, ensure single-use via Redis JTI blacklist,
    and activate user's verified status.
    """
    payload = decode_verification_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token.")
        
    jti = payload.get("jti")
    if jti and await redis_store.is_jti_blacklisted(jti):
        raise HTTPException(status_code=400, detail="Verification token has already been used.")
        
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid verification token payload.")
        
    statement = select(User).where(User.id == user_id)
    result = await db.exec(statement)
    user = result.first()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found or inactive.")
        
    if user.is_verified:
        return {"message": "Email is already verified. You can now log in."}
        
    # Mark user as verified
    user.is_verified = True
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Blacklist token JTI (single-use token protection)
    if jti:
        await redis_store.blacklist_jti(jti, 86400) # 24 hour TTL
        
    audit_log.auth_event("email_verified", user_id=str(user.id), email=user.email or "")
    return {"message": "Email verified successfully! You can now log in."}

@router.post("/resend-verification", dependencies=[Depends(resend_verification_rate_limiter)])
async def resend_verification(
    request: ResendVerificationRequest,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Resend verification email. Always returns a generic response to prevent account enumeration.
    """
    statement = select(User).where(User.email == request.email)
    result = await db.exec(statement)
    user = result.first()
    
    verify_url = None
    if user and user.is_active and user.email and not user.is_verified:
        token = create_verification_token(user.id)
        verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        email_res = await send_verification_email(user.email, verify_url)
        if settings.ENVIRONMENT != "production" and email_res.get("verify_url"):
            verify_url = email_res.get("verify_url")
        logger.info(f"Resent verification email to {user.email}")
        
    response_payload = {
        "message": "If an account with this email exists and requires verification, a new link has been sent."
    }
    if settings.ENVIRONMENT != "production" and verify_url:
        response_payload["dev_verify_url"] = verify_url

    return response_payload

# --- 3. LOGIN & VERIFICATION GUARD ---

@router.post("/login", dependencies=[Depends(login_rate_limiter)])
async def login_access_token(
    response: Response,
    remember_me: bool = Query(default=True),
    db: AsyncSession = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 password login with login-verification guard and token-version binding.
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
        
    # Email verification guard: standard email accounts must be verified before login
    if user.email and not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your inbox or request a new verification link."
        )
        
    new_refresh = create_refresh_token(user.id, token_version=user.token_version)
    set_refresh_cookie(response, new_refresh, remember_me=remember_me)

    audit_log.auth_event("login_success", user_id=str(user.id), email=user.email or "")
    
    return {
        "access_token": create_access_token(user.id, token_version=user.token_version),
        "token_type": "bearer",
    }

# --- 4. REFRESH TOKEN ROTATION (HTTPONLY COOKIE STRICT) ---

@router.post("/refresh")
async def refresh_access_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Silent refresh using HttpOnly cookie.
    Validates token signature, type=='refresh', JTI revocation, and user token_version.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
        
    payload = decode_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    jti = payload.get("jti")
    if jti and await redis_store.is_jti_blacklisted(jti):
        raise HTTPException(status_code=401, detail="Refresh token has been revoked")
        
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    statement = select(User).where(User.id == user_id)
    result = await db.exec(statement)
    user = result.first()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
        
    # Token-version session invalidation check
    token_version = payload.get("token_version", 1)
    if user.token_version != token_version:
        raise HTTPException(status_code=401, detail="Session expired or invalidated. Please log in again.")
        
    # Rotate refresh token: blacklist previous JTI
    if jti:
        expiry_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        await redis_store.blacklist_jti(jti, expiry_seconds)
        
    new_refresh = create_refresh_token(user.id, token_version=user.token_version)
    set_refresh_cookie(response, new_refresh)
    
    return {
        "access_token": create_access_token(user.id, token_version=user.token_version),
        "token_type": "bearer",
    }

# --- 5. PASSWORD RESET & GLOBAL SESSION REVOCATION ---

@router.post("/forgot-password", dependencies=[Depends(forgot_password_rate_limiter)])
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Generate single-use password reset token with uniform generic response.
    """
    statement = select(User).where(User.email == request.email)
    result = await db.exec(statement)
    user = result.first()
    
    reset_url = None
    if user and user.is_active and user.email:
        token = create_reset_token(user.id)
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        email_res = await send_password_reset_email(user.email, reset_url)
        if settings.ENVIRONMENT != "production" and email_res.get("reset_url"):
            reset_url = email_res.get("reset_url")
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
    Verify reset token, ensure password strength and difference,
    update password, increment token_version to invalidate all existing sessions,
    and blacklist the reset token JTI.
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
        
    # Enforce password strength
    validate_password(req.new_password)
    
    # Ensure new password is not identical to old password
    if user.hashed_password and verify_password(req.new_password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="New password cannot be the same as your old password."
        )
        
    # Update password and increment token_version (C-03 / Section 10: Invalidate all existing sessions)
    user.hashed_password = get_password_hash(req.new_password)
    user.token_version += 1
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Blacklist the reset token so it cannot be reused
    if jti:
        await redis_store.blacklist_jti(jti, settings.RESET_TOKEN_EXPIRE_MINUTES * 60)
        
    audit_log.auth_event("password_reset_complete", user_id=str(user.id), email=user.email or "")
    return {"message": "Password updated successfully. You can now log in with your new password."}

# --- 6. GUEST ACCOUNT CREATION & SECURE CONVERSION ---

@router.post("/guest", dependencies=[Depends(guest_rate_limiter)])
async def create_guest_user(
    response: Response,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Create a guest user session.
    """
    user = User(is_guest=True, is_active=True, is_verified=False, token_version=1)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    new_refresh = create_refresh_token(user.id, token_version=user.token_version)
    set_refresh_cookie(response, new_refresh)

    audit_log.auth_event("guest_created", user_id=str(user.id))
    
    return {
        "access_token": create_access_token(user.id, token_version=user.token_version),
        "token_type": "bearer",
        "user_id": user.id
    }

@router.post("/convert-guest")
async def convert_guest_account(
    req: UserRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Convert an active guest account into a permanent verified account.
    Maintains user ID and all historical scraping sessions and datasets.
    """
    if not current_user.is_guest:
        raise HTTPException(status_code=400, detail="Current account is not a guest account.")
        
    validate_password(req.password)
    
    # Ensure desired email is not taken
    statement = select(User).where(User.email == req.email)
    result = await db.exec(statement)
    existing_user = result.first()
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system."
        )
        
    # Convert guest record in-place to preserve all ownership links
    current_user.email = req.email
    current_user.full_name = req.full_name
    current_user.hashed_password = get_password_hash(req.password)
    current_user.is_guest = False
    current_user.is_verified = False
    current_user.token_version += 1
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    # Send verification email for the new permanent account
    verify_token = create_verification_token(current_user.id)
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={verify_token}"
    email_res = await send_verification_email(req.email, verify_url)
    
    response_payload = {
        "message": "Guest account converted successfully! Please verify your email before logging in again."
    }
    if settings.ENVIRONMENT != "production" and email_res.get("verify_url"):
        response_payload["dev_verify_url"] = email_res.get("verify_url")

    return response_payload

# --- 7. OAUTH: GOOGLE & PHONE LOGIN ---

@router.post("/google")
async def login_google(
    request: TokenRequest,
    response: Response,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Login or register via Google OAuth ID token.
    Enforces verified-email claim to prevent account takeover.
    """
    try:
        idinfo = verify_google_token(request.id_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    email = idinfo.get("email")
    google_id = idinfo.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Google token does not contain a valid email.")
        
    statement = select(User).where((User.google_id == google_id) | (User.email == email))
    result = await db.exec(statement)
    user = result.first()
    
    if not user:
        # New Google user: Google has already verified this email
        user = User(
            email=email,
            google_id=google_id,
            is_active=True,
            is_verified=True,
            token_version=1
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        # Safe linking: mark verified because Google verified this email address
        if not user.google_id:
            user.google_id = google_id
        user.is_verified = True
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    new_refresh = create_refresh_token(user.id, token_version=user.token_version)
    set_refresh_cookie(response, new_refresh)
    
    return {
        "access_token": create_access_token(user.id, token_version=user.token_version),
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
        user = User(phone_number=phone_number, is_active=True, is_verified=True, token_version=1)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    new_refresh = create_refresh_token(user.id, token_version=user.token_version)
    set_refresh_cookie(response, new_refresh)
        
    return {
        "access_token": create_access_token(user.id, token_version=user.token_version),
        "token_type": "bearer",
    }

# --- 8. CURRENT USER & LOGOUT ---

@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get authenticated user profile."""
    return current_user

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Logout by invalidating the refresh token and clearing cookie.
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        payload = decode_refresh_token(refresh_token)
        if payload and payload.get("jti"):
            jti = str(payload.get("jti"))
            expiry_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
            await redis_store.blacklist_jti(jti, expiry_seconds)
            
    clear_refresh_cookie(response)
    audit_log.auth_event("logout", user_id=str(current_user.id), email=current_user.email or "")
    return {"message": "Successfully logged out"}
