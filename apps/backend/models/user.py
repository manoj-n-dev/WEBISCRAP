from sqlmodel import Field, SQLModel
from typing import Optional
from .base import BaseUUIDModel

class UserBase(SQLModel):
    email: Optional[str] = Field(default=None, unique=True, index=True)
    phone_number: Optional[str] = Field(default=None, unique=True, index=True)
    google_id: Optional[str] = Field(default=None, unique=True, index=True)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_guest: bool = Field(default=False)
    
class User(UserBase, BaseUUIDModel, table=True):
    __tablename__ = "users"
    hashed_password: Optional[str] = Field(default=None)

class UserCreate(UserBase):
    password: Optional[str] = None

from datetime import datetime
import uuid

class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
