from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text
from uuid import UUID, uuid4
from datetime import datetime


class Todo(SQLModel, table=True):
    """Todo model representing a task item belonging to a user."""

    __tablename__ = "todos"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=500)
    completed: bool = Field(default=False)
    # user_id references Better Auth's "user" table (text ID)
    user_id: str = Field(sa_column=Column(Text, index=True, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
