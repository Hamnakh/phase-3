from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    name: str | None = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    email: str
    name: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
