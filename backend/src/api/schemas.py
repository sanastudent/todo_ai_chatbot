from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class ChatRequest(BaseModel):
    """
    Request schema for chat endpoint
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's natural language message"
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Optional conversation ID to continue existing conversation. If omitted, a new conversation will be created."
    )


class ChatResponse(BaseModel):
    """
    Response schema for chat endpoint
    """
    response: str = Field(
        ...,
        description="AI assistant's natural language response"
    )
    conversation_id: str = Field(
        ...,
        description="Conversation ID (for subsequent messages)"
    )
    message_id: str = Field(
        ...,
        description="Unique ID of the assistant's message"
    )


class ErrorResponse(BaseModel):
    """
    Error response schema
    """
    error: str = Field(
        ...,
        description="User-friendly error message"
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Conversation ID (if available)"
    )