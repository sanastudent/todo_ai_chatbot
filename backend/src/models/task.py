from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional, List
from uuid import uuid4
import json


from sqlalchemy import UniqueConstraint

class Task(SQLModel, table=True):
    """
    Represents a todo item that a user wants to track, with additional fields for priority, tags, and improved search capabilities.
    """
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False, nullable=False)
    priority: str = Field(default="medium", max_length=10, nullable=False)  # ENUM('high', 'medium', 'low')
    category: str = Field(default="general", max_length=50, nullable=False)  # ENUM('work', 'personal', 'general', etc.)
    due_date: Optional[datetime] = Field(default=None, nullable=True)
    # Store tags as JSON string in the database, handle serialization/deserialization in the application
    tags: str = Field(default="[]", max_length=2000, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Add unique constraint to prevent duplicate tasks for the same user with the same title
    __table_args__ = (UniqueConstraint('user_id', 'title', name='unique_user_task'), {'sqlite_autoincrement': True})