from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class MessageCreate(BaseModel):
    """Schema for creating a new message (user input)."""
    content: str


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    tool_calls: Optional[List[dict]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    id: UUID
    user_id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Schema for conversation with all messages."""
    messages: List[MessageResponse] = []


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str
    conversation_id: Optional[UUID] = None


class ChatResponse(BaseModel):
    """Schema for chat response."""
    conversation_id: UUID
    message: MessageResponse
    assistant_message: MessageResponse
