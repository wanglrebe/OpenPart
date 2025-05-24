# backend/app/auth/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.auth.models import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.ADMIN

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True