from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional
from uuid import uuid4
from datetime import datetime
from sqlalchemy import select
import logging
import traceback

from src.api.schemas import ChatRequest, ChatResponse, ErrorResponse
from src.api.deps import get_db_session, get_current_user
from src.models.conversation import Conversation
from src.models.message import Message
from src.services.agent import invoke_agent
from src.mcp.tools import add_task, list_tasks, complete_task, update_task, delete_task


router = APIRouter()

# Set up logging
logger = logging.getLogger(__name__)


async def get_message_history(db_session: AsyncSession, conversation_id: str):
    """
    Load message history for a conversation ordered by created_at
    """
    try:
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())

        results = await db_session.exec(statement)
        messages = results.all()
        return messages
    except Exception as e:
        logger.error(f"Error loading message history for conversation {conversation_id}: {str(e)}")
        logger.error(f"Full traceback in get_message_history: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="Error loading message history"
        )


@router.get("/api/health")
async def api_health_check():
    """
    API health check endpoint to verify the API is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "api"
    }


@router.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    chat_request: ChatRequest,
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Chat endpoint that handles conversation persistence
    """
    # For now, use the path user_id as the authenticated user
    # In a real implementation, this would validate the user from auth headers
    current_user = user_id

    conversation_id = chat_request.conversation_id
    conversation: Optional[Conversation] = None

    try:
        # Validate user_id
        if not user_id or not user_id.strip():
            raise HTTPException(
                status_code=400,
                detail="User ID is required and cannot be empty"
            )

        # Validate message
        if not chat_request.message or not chat_request.message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message is required and cannot be empty"
            )

        # If conversation_id provided, try to load existing conversation
        if conversation_id:
            conversation = await db_session.get(Conversation, conversation_id)
            if not conversation:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found"
                )
            if conversation.user_id != user_id:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied: You don't own this conversation"
                )
        else:
            # Create new conversation if no conversation_id provided
            conversation = Conversation(
                id=str(uuid4()),
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db_session.add(conversation)
            await db_session.commit()
            await db_session.refresh(conversation)
            conversation_id = conversation.id

        # Load message history for the conversation
        message_history = await get_message_history(db_session, conversation_id)

        # Save user message
        user_message = Message(
            id=str(uuid4()),
            user_id=user_id,
            conversation_id=conversation_id,
            role="user",
            content=chat_request.message,
            created_at=datetime.utcnow()
        )
        db_session.add(user_message)
        await db_session.commit()

        # Call the AI agent to generate response
        # This replaces the stub response with actual agent invocation
        response_text = await invoke_agent(
            user_id=user_id,
            conversation_id=conversation_id,
            user_message=chat_request.message,
            db_session=db_session
        )

        # Save assistant message
        assistant_message = Message(
            id=str(uuid4()),
            user_id=user_id,
            conversation_id=conversation_id,
            role="assistant",
            content=response_text,
            created_at=datetime.utcnow()
        )
        db_session.add(assistant_message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        db_session.add(conversation)

        # Commit all changes at the end
        await db_session.commit()
        await db_session.refresh(assistant_message)

        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            message_id=assistant_message.id
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the full error with traceback for debugging
        import traceback
        logger.error(f"Error processing chat request for user {user_id}: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")

        # Ensure conversation_id is defined before returning error response
        safe_conversation_id = conversation_id if conversation_id else None

        # Return a user-friendly error response while preserving conversation_id if available
        return ErrorResponse(
            error="An error occurred while processing your request. Please try again.",
            conversation_id=safe_conversation_id
        )


@router.post("/api/{user_id}/tasks")
async def create_task(
    user_id: str,
    request_data: dict,
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Create a new task for the user
    Expected payload: {"title": "...", "description": "...", "priority": "...", "tags": [...]}
    """
    try:
        title = request_data.get("title")
        description = request_data.get("description")
        priority = request_data.get("priority")
        tags = request_data.get("tags")

        result = await add_task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            db_session=db_session
        )

        return result
    except Exception as e:
        logger.error(f"Error creating task for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    completed: Optional[bool] = None,
    priority: str = None,
    tags: str = None,
    search_term: str = None,
    date_from: str = None,
    date_to: str = None,
    sort_by: str = None,
    sort_order: str = None,
    limit: int = 50,
    offset: int = 0,
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Get tasks for the user with optional filters
    """
    from datetime import datetime

    try:
        # Parse priority list if provided
        priority_list = None
        if priority:
            priority_list = [p.strip() for p in priority.split(",")]

        # Parse tags list if provided
        tags_list = None
        if tags:
            tags_list = [t.strip() for t in tags.split(",")]

        # Parse dates if provided
        parsed_date_from = datetime.fromisoformat(date_from) if date_from else None
        parsed_date_to = datetime.fromisoformat(date_to) if date_to else None

        result = await list_tasks(
            user_id=user_id,
            completed=completed,
            priority=priority_list,
            tags=tags_list,
            search_term=search_term,
            date_from=parsed_date_from,
            date_to=parsed_date_to,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
            db_session=db_session
        )

        return result
    except Exception as e:
        logger.error(f"Error retrieving tasks for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/{user_id}/tasks/{task_id}/complete")
async def mark_task_complete(
    user_id: str,
    task_id: str,
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Mark a task as completed
    """
    try:
        result = await complete_task(
            user_id=user_id,
            task_id=task_id,
            db_session=db_session
        )

        return result
    except Exception as e:
        logger.error(f"Error completing task {task_id} for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/{user_id}/tasks/{task_id}")
async def update_existing_task(
    user_id: str,
    task_id: str,
    request_data: dict,
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Update an existing task
    Expected payload: {"title": "...", "description": "...", "priority": "...", "tags": [...]}
    """
    try:
        title = request_data.get("title")
        description = request_data.get("description")
        priority = request_data.get("priority")
        tags = request_data.get("tags")

        result = await update_task(
            user_id=user_id,
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            db_session=db_session
        )

        return result
    except Exception as e:
        logger.error(f"Error updating task {task_id} for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/{user_id}/tasks/{task_id}")
async def remove_task(
    user_id: str,
    task_id: str,
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Delete a task
    """
    try:
        result = await delete_task(
            user_id=user_id,
            task_id=task_id,
            db_session=db_session
        )

        return result
    except Exception as e:
        logger.error(f"Error deleting task {task_id} for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))