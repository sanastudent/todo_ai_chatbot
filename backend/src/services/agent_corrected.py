from typing import Dict, Any, List, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import logging
import os
from datetime import datetime
import httpx
import json
from openai import AsyncOpenAI

from src.models.message import Message
from src.models.conversation import Conversation
from src.mcp.tools import add_task, list_tasks, complete_task, update_task, delete_task

logger = logging.getLogger(__name__)

# OpenAI client will be initialized lazily when needed
openai_api_key = os.getenv("OPENAI_API_KEY")


def get_mcp_tool_schemas():
    """
    Define the function schemas for MCP tools to be used with OpenAI function calling
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task for the user. Call this when the user wants to add, create, or remember something they need to do.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user"},
                        "title": {"type": "string", "description": "The title of the task"},
                        "description": {"type": "string", "description": "Detailed description of the task"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Priority level of the task"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags associated with the task"}
                    },
                    "required": ["user_id", "title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "Retrieve all tasks for the user, optionally filtered by completion status. Call this when the user wants to see, show, list, or view their tasks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user"},
                        "completed": {"type": "boolean", "description": "Filter by completion status. True for completed, False for pending, null for all"},
                        "priority": {"type": "array", "items": {"type": "string"}, "description": "Filter by priority levels"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
                        "search_term": {"type": "string", "description": "Search term to filter tasks by title or description"},
                        "date_from": {"type": "string", "description": "Filter tasks created after this date (ISO format)"},
                        "date_to": {"type": "string", "description": "Filter tasks created before this date (ISO format)"},
                        "sort_by": {"type": "string", "description": "Field to sort by (created_at, priority, etc.)"},
                        "sort_order": {"type": "string", "enum": ["asc", "desc"], "description": "Sort order"},
                        "limit": {"type": "integer", "description": "Maximum number of tasks to return"},
                        "offset": {"type": "integer", "description": "Offset for pagination"}
                    },
                    "required": ["user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as completed. Call this when the user says they finished, completed, or are done with a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user"},
                        "task_id": {"type": "string", "description": "The ID of the task to mark as completed"}
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update the title or description of an existing task. Call this when the user wants to modify, change, or update details of a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user"},
                        "task_id": {"type": "string", "description": "The ID of the task to update"},
                        "title": {"type": "string", "description": "New title for the task"},
                        "description": {"type": "string", "description": "New description for the task"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "New priority level"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "New tags for the task"}
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task. Call this when the user wants to remove, delete, or cancel a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user"},
                        "task_id": {"type": "string", "description": "The ID of the task to delete"}
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        }
    ]


async def get_conversation_history(db_session: AsyncSession, conversation_id: str) -> List[Dict[str, str]]:
    """
    Retrieve the conversation history for a given conversation ID
    """
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc())

    results = await db_session.exec(statement)
    messages = results.all()

    history = []
    for message in messages:
        history.append({
            "role": message.role,
            "content": message.content
        })

    return history


async def call_openai_agent(message: str, user_id: str, conversation_history: List[Dict[str, str]]) -> str:
    """
    Call the OpenAI agent with MCP tools for task management
    """
    try:
        client = AsyncOpenAI(
            api_key=openai_api_key
            # NO 'proxies' parameter here - it causes TypeError in newer openai library
        )

        # Prepare the conversation messages
        system_prompt = """You are an AI assistant for a task management application. Help users manage their tasks by understanding their natural language requests and using the appropriate tools.
        - Use add_task to create new tasks when users want to add, remember, or create something
        - Use list_tasks to show users their tasks when they ask to see, show, list, or view tasks
        - Use complete_task to mark tasks as done when users say they finished, completed, or are done with something
        - Use update_task to modify existing tasks when users want to change details
        - Use delete_task to remove tasks when users want to eliminate them
        Be helpful and conversational in your responses."""

        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # Add conversation history
        messages.extend(conversation_history)

        # Add the current user message
        messages.append({"role": "user", "content": message})

        # Call OpenAI with function calling
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # or whatever model is preferred
            messages=messages,
            tools=get_mcp_tool_schemas(),
            tool_choice="auto"
        )

        # Process the response
        response_message = response.choices[0].message

        # Handle tool calls if any
        tool_calls = response_message.tool_calls
        if tool_calls:
            # Process each tool call
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Ensure user_id is passed to all tool calls
                function_args["user_id"] = user_id

                try:
                    if function_name == "add_task":
                        result = await add_task(**function_args, db_session=db_session)
                        tool_response = str(result)
                    elif function_name == "list_tasks":
                        result = await list_tasks(**function_args, db_session=db_session)
                        tool_response = str(result)
                    elif function_name == "complete_task":
                        result = await complete_task(**function_args, db_session=db_session)
                        tool_response = str(result)
                    elif function_name == "update_task":
                        result = await update_task(**function_args, db_session=db_session)
                        tool_response = str(result)
                    elif function_name == "delete_task":
                        result = await delete_task(**function_args, db_session=db_session)
                        tool_response = str(result)
                    else:
                        tool_response = f"Unknown function: {function_name}"

                    # Add the tool response to messages for the final response
                    messages.append({
                        "role": "tool",
                        "content": tool_response,
                        "tool_call_id": tool_call.id
                    })

                except Exception as e:
                    logger.error(f"Error calling tool {function_name}: {str(e)}")
                    messages.append({
                        "role": "tool",
                        "content": f"Error: {str(e)}",
                        "tool_call_id": tool_call.id
                    })

            # Get the final response from the assistant
            final_response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            return final_response.choices[0].message.content

        else:
            # If no tools were called, return the assistant's response directly
            return response_message.content

    except Exception as e:
        logger.error(f"Error calling OpenAI agent: {str(e)}")
        raise


async def invoke_agent(
    user_id: str,
    conversation_id: str,
    user_message: str,
    db_session: AsyncSession
) -> str:
    """
    Main function to invoke the AI agent - this routes ALL user messages to the OpenAI agent
    which will use MCP tools for task management operations
    """
    try:
        # Get conversation history for context
        conversation_history = await get_conversation_history(db_session, conversation_id)

        # Call the OpenAI agent to process the message and use MCP tools as needed
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            response_text = await call_openai_agent(
                message=user_message,
                user_id=user_id,
                conversation_history=conversation_history
            )
        else:
            # If no OpenAI API key is configured, raise an error since we don't want mock responses
            raise Exception("OpenAI API key not configured. Real AI agent required for proper functionality.")

        return response_text

    except Exception as e:
        logger.error(f"Error in invoke_agent: {str(e)}")
        raise