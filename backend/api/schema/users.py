from datetime import datetime

from pydantic import BaseModel, EmailStr

from backend.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole


class AgentUserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None
    is_active: bool | None = None


class AdminUserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
