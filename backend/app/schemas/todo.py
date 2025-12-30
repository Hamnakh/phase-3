from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class TodoCreate(BaseModel):
    """Schema for creating a new todo."""
    title: str = Field(..., min_length=1, max_length=500)


class TodoUpdate(BaseModel):
    """Schema for updating a todo."""
    title: str | None = Field(None, min_length=1, max_length=500)
    completed: bool | None = None


class TodoResponse(BaseModel):
    """Schema for todo response."""
    id: UUID
    title: str
    completed: bool
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
