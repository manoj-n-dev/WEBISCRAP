from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import Any

from database.connection import get_session
from models.user import User, UserCreate, UserRead
from auth.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from auth.dependencies import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserRead)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Register a new user.
    """
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
    db: AsyncSession = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    statement = select(User).where(User.email == form_data.username)
    result = await db.exec(statement)
    user = result.first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
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

from pydantic import BaseModel
from auth.providers import verify_google_token, verify_firebase_token

class TokenRequest(BaseModel):
    id_token: str

@router.post("/google")
async def login_google(
    request: TokenRequest,
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
        
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }

@router.post("/phone")
async def login_phone(
    request: TokenRequest,
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
        
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }
