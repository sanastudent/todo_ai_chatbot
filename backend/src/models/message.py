from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional
from uuid import uuid4


class Message(SQLModel, table=True):
    """
    Represents a single message in a conversation (user or assistant)
    """
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    conversation_id: str = Field(foreign_key="conversation.id", index=True, nullable=False)
    role: str = Field(nullable=False)  # 'user' or 'assistant'
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")