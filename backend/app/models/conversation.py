from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List
import json


class Conversation(SQLModel, table=True):
    """Conversation model representing a chat session for a user."""

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(sa_column=Column(Text, index=True, nullable=False))
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    """Message model representing a single message in a conversation."""

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    content: str = Field(sa_column=Column(Text, nullable=False))
    # Store tool calls as JSON string
    tool_calls: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to conversation
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    def get_tool_calls(self) -> Optional[list]:
        """Parse tool_calls JSON string to list."""
        if self.tool_calls:
            return json.loads(self.tool_calls)
        return None

    def set_tool_calls(self, calls: list) -> None:
        """Set tool_calls as JSON string."""
        self.tool_calls = json.dumps(calls) if calls else None
