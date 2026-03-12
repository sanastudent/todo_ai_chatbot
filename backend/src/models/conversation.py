from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional, List
from uuid import uuid4


class Conversation(SQLModel, table=True):
    """
    Represents a chat session between user and AI assistant
    """
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship
    messages: List["Message"] = Relationship(back_populates="conversation")