from sqlmodel import Field, SQLModel
from typing import Optional, Any
from pydantic import field_validator
from datetime import datetime
import re
import uuid
from .base import BaseUUIDModel

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

class UserBase(SQLModel):
    email: Optional[str] = Field(default=None, unique=True, index=True)
    full_name: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None, unique=True, index=True)
    google_id: Optional[str] = Field(default=None, unique=True, index=True)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_guest: bool = Field(default=False)
    is_verified: bool = Field(default=False, index=True)
    token_version: int = Field(default=1)
    
class User(UserBase, BaseUUIDModel, table=True):
    __tablename__: Any = "users"  # type: ignore
    hashed_password: Optional[str] = Field(default=None)

class UserRegisterRequest(SQLModel):
    """Strict registration DTO: excludes all privileged account controls."""
    email: str
    password: str
    full_name: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError("Invalid email address format.")
        return clean

class UserCreate(UserBase):
    password: Optional[str] = None

class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
