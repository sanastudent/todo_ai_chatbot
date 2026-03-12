from typing import Dict, Any, List, Optional, Tuple
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import logging
import os
from datetime import datetime
import httpx
import json
import traceback
from openai import AsyncOpenAI

from src.models.message import Message
from src.models.conversation import Conversation
from src.mcp.tools import add_task, list_tasks, complete_task, update_task, delete_task

logger = logging.getLogger(__name__)

# OpenAI client will be initialized lazily when needed
openai_api_key = os.getenv("OPENAI_API_KEY")

# CONVERSATION CONTEXT FIX: In-memory storage for pending operations
# Maps conversation_id -> pending operation details
_pending_operations: Dict[str, Dict[str, Any]] = {}

# PERFORMANCE OPTIMIZATION: Task list cache to reduce repeated database calls
# Maps user_id -> (task_list, timestamp)
_task_list_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
_CACHE_TTL_SECONDS = 30  # Cache task list for 30 seconds


def set_pending_operation(conversation_id: str, operation_type: str, task_id: str, task_title: str, pending_field: Optional[str] = None):
    """Store a pending operation that requires user confirmation or additional input."""
    _pending_operations[conversation_id] = {
        "operation_type": operation_type,  # "delete", "update_description", "update_title", etc.
        "task_id": task_id,
        "task_title": task_title,
        "pending_field": pending_field  # What we're waiting for: "confirmation", "description", "title", etc.
    }
    logger.info(f"Set pending operation for conversation {conversation_id}: {operation_type} on task {task_id}")


def get_pending_operation(conversation_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve the pending operation for a conversation."""
    return _pending_operations.get(conversation_id)


def clear_pending_operation(conversation_id: str):
    """Clear the pending operation after it's completed or cancelled."""
    if conversation_id in _pending_operations:
        logger.info(f"Cleared pending operation for conversation {conversation_id}")
        del _pending_operations[conversation_id]


def invalidate_task_cache(user_id: str):
    """
    PERFORMANCE OPTIMIZATION: Invalidate task list cache for a user.
    Called when tasks are added, updated, completed, or deleted.
    """
    if user_id in _task_list_cache:
        logger.debug(f"Invalidated task cache for user {user_id}")
        del _task_list_cache[user_id]


def get_cached_task_list(user_id: str) -> Optional[Dict[str, Any]]:
    """
    PERFORMANCE OPTIMIZATION: Get cached task list if available and not expired.
    Returns None if cache miss or expired.
    """
    import time
    if user_id in _task_list_cache:
        task_list, timestamp = _task_list_cache[user_id]
        age = time.time() - timestamp
        if age < _CACHE_TTL_SECONDS:
            logger.debug(f"Task cache HIT for user {user_id} (age: {age:.1f}s)")
            return task_list
        else:
            logger.debug(f"Task cache EXPIRED for user {user_id} (age: {age:.1f}s)")
            del _task_list_cache[user_id]
    return None


def set_cached_task_list(user_id: str, task_list: Dict[str, Any]):
    """
    PERFORMANCE OPTIMIZATION: Cache task list for a user.
    """
    import time
    _task_list_cache[user_id] = (task_list, time.time())
    logger.debug(f"Task cache SET for user {user_id}")


async def handle_pending_operation(conversation_id: str, user_message: str, user_id: str, db_session: AsyncSession) -> Optional[str]:
    """
    Check if there's a pending operation and handle the user's response.
    Returns the response if a pending operation was handled, None otherwise.
    """
    pending = get_pending_operation(conversation_id)
    if not pending:
        return None

    operation_type = pending["operation_type"]
    task_id = pending["task_id"]
    task_title = pending["task_title"]
    pending_field = pending["pending_field"]

    message_lower = user_message.lower().strip()

    # Handle confirmation responses (yes/no)
    if pending_field == "confirmation":
        if message_lower in ["yes", "y", "yeah", "yep", "sure", "ok", "okay", "proceed", "confirm"]:
            # User confirmed - execute the operation
            try:
                if operation_type == "delete":
                    result = await delete_task(user_id=user_id, task_id=task_id, db_session=db_session)
                    # PERFORMANCE: Invalidate cache after deleting task
                    invalidate_task_cache(user_id)
                    clear_pending_operation(conversation_id)
                    return f"✅ Task '{task_title}' has been deleted successfully."
                elif operation_type == "complete":
                    result = await complete_task(user_id=user_id, task_id=task_id, db_session=db_session)
                    # PERFORMANCE: Invalidate cache after completing task
                    invalidate_task_cache(user_id)
                    clear_pending_operation(conversation_id)
                    return f"✅ Task '{task_title}' has been marked as completed."
            except Exception as e:
                clear_pending_operation(conversation_id)
                return f"❌ Error executing operation: {str(e)}"
        elif message_lower in ["no", "n", "nope", "cancel", "nevermind", "never mind"]:
            # User cancelled
            clear_pending_operation(conversation_id)
            return f"Operation cancelled. Task '{task_title}' was not modified."
        else:
            # Unclear response - ask again
            return f"Please respond with 'yes' to confirm or 'no' to cancel the operation on task '{task_title}'."

    # Handle description update
    elif pending_field == "description":
        # User provided the new description
        new_description = user_message.strip()
        # Remove common prefixes like "Description:", "New description:", etc.
        import re
        new_description = re.sub(r'^(description|new description|desc):\s*', '', new_description, flags=re.IGNORECASE)

        try:
            result = await update_task(user_id=user_id, task_id=task_id, description=new_description, db_session=db_session)
            # PERFORMANCE: Invalidate cache after updating task
            invalidate_task_cache(user_id)
            clear_pending_operation(conversation_id)
            return f"✅ Task '{task_title}' description has been updated to: '{new_description}'"
        except Exception as e:
            clear_pending_operation(conversation_id)
            return f"❌ Error updating task description: {str(e)}"

    # Handle title/rename update
    elif pending_field == "title":
        # User provided the new title
        new_title = user_message.strip()
        # Remove common prefixes like "Title:", "New title:", "Rename to:", etc.
        import re
        new_title = re.sub(r'^(title|new title|rename to|name):\s*', '', new_title, flags=re.IGNORECASE)

        try:
            result = await update_task(user_id=user_id, task_id=task_id, title=new_title, db_session=db_session)
            # PERFORMANCE: Invalidate cache after updating task
            invalidate_task_cache(user_id)
            clear_pending_operation(conversation_id)
            return f"✅ Task '{task_title}' has been renamed to: '{new_title}'"
        except Exception as e:
            clear_pending_operation(conversation_id)
            return f"❌ Error renaming task: {str(e)}"

    # Unknown pending field - clear and return None
    clear_pending_operation(conversation_id)
    return None


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


async def parse_basic_command(message: str, user_id: str, db_session: AsyncSession) -> Optional[str]:
    """
    Parse and execute basic commands when AI is not available.
    Returns the response string if a command was parsed, None otherwise.
    """
    import re

    message_lower = message.lower().strip()

    # Command: add [task]
    # Matches: "add buy milk", "add a new task", "add task to buy milk", "add buy fresh fruits to the tasks"
    add_patterns = [
        r'^add\s+(?:a\s+)?(?:new\s+)?(?:task\s+)?(?:to\s+)?(?:the\s+)?(?:tasks?\s+)?(?:my\s+)?(.+?)(?:\s+to\s+(?:the\s+)?tasks?)?$',
        r'^create\s+(?:a\s+)?(?:new\s+)?(?:task\s+)?(?:to\s+)?(?:the\s+)?(?:tasks?\s+)?(?:my\s+)?(.+?)(?:\s+to\s+(?:the\s+)?tasks?)?$',
        r'^(?:i\s+)?(?:need\s+to|want\s+to|have\s+to)\s+(.+)$',
    ]

    for pattern in add_patterns:
        match = re.match(pattern, message_lower, re.IGNORECASE)
        if match:
            task_title = match.group(1).strip()

            # Remove trailing filler words
            task_title = re.sub(r'\s+to\s+(?:the\s+)?tasks?$', '', task_title, flags=re.IGNORECASE)

            # Remove any remaining leading/trailing filler words
            # This handles cases where filler words weren't caught by the regex
            while True:
                old_title = task_title
                task_title = re.sub(r'^(?:a|an|the|new|task|tasks|my|to)\s+', '', task_title, flags=re.IGNORECASE)
                task_title = re.sub(r'\s+(?:a|an|the|new|task|tasks|my|to)$', '', task_title, flags=re.IGNORECASE)
                task_title = task_title.strip()
                if task_title == old_title:
                    break  # No more changes

            # If only filler words remain or empty, use a generic task name
            if not task_title or task_title.lower() in ['a', 'an', 'the', 'task', 'tasks', 'new', 'my', 'to']:
                task_title = 'new task'

            try:
                result = await add_task(
                    user_id=user_id,
                    title=task_title,
                    db_session=db_session
                )
                return f"✅ Task added: '{task_title}'\n\nYou can view your tasks by typing 'list tasks'."
            except Exception as e:
                logger.error(f"Error adding task: {str(e)}")
                return f"❌ Sorry, I couldn't add the task. Error: {str(e)}"

    # Helper to format task list response
    async def _fetch_and_format_tasks(completed_filter=None, label="Your tasks"):
        result = await list_tasks(user_id=user_id, completed=completed_filter, db_session=db_session)
        if isinstance(result, dict) and 'tasks' in result:
            tasks = result['tasks']
            if not tasks:
                if completed_filter is False:
                    return "📋 No pending tasks! You're all caught up.\n\nAdd a task by typing: 'add [task description]'"
                elif completed_filter is True:
                    return "📋 No completed tasks yet."
                return "📋 You have no tasks yet.\n\nAdd a task by typing: 'add [task description]'"
            response = f"📋 {label}:\n\n"
            for i, task in enumerate(tasks, 1):
                status = "✅" if task.get('completed') else "⬜"
                priority = task.get('priority', '')
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "")
                title = task.get('title', 'Untitled')
                response += f"{i}. {status} {priority_icon} {title}\n"
            response += "\n💡 Type 'complete task [number]' to mark a task done."
            return response
        return str(result)

    # Command: list pending tasks
    # Matches: "show pending tasks", "what do I need to do today?", "what's left on my list", etc.
    pending_patterns = [
        r'^(?:list|show|view|display|get|see)(?:\s+me)?(?:\s+my)?(?:\s+all)?(?:\s+the)?\s+pending(?:\s+tasks?)?$',
        r'^(?:pending|incomplete|todo|to-do|to\s+do)(?:\s+tasks?)?$',
        r'^what(?:\s+do|\s+should)?\s+(?:i|we)\s+(?:need\s+to\s+do|have\s+to\s+do|should\s+do|need\s+to\s+complete)(?:\s+today)?[\s?]*$',
        r"^what(?:'s|\s+is|\s+are)\s+(?:left|remaining|pending)(?:\s+on\s+my\s+(?:list|todo|tasks?))?[\s?]*$",
        r'^(?:show|list|what\s+are)\s+my\s+(?:pending|remaining|incomplete|active)\s+tasks?[\s?]*$',
        r'^(?:what\s+should\s+i\s+do|what\s+are\s+my\s+tasks?)[\s?]*$',
    ]
    for pattern in pending_patterns:
        if re.match(pattern, message_lower, re.IGNORECASE):
            try:
                return await _fetch_and_format_tasks(completed_filter=False, label="Pending tasks")
            except Exception as e:
                logger.error(f"Error listing pending tasks: {str(e)}")
                return f"❌ Sorry, I couldn't list your tasks. Error: {str(e)}"

    # Command: list all tasks
    # Matches: "list", "list tasks", "show tasks", "show my tasks", "list all the tasks"
    all_tasks_pattern = r'^(?:list|show|view|display|get|see)(?:\s+me)?(?:\s+my)?(?:\s+all)?(?:\s+the)?(?:\s+my)?(?:\s+tasks?)?$'
    if re.match(all_tasks_pattern, message_lower):
        try:
            return await _fetch_and_format_tasks(label="Your tasks")
        except Exception as e:
            logger.error(f"Error listing tasks: {str(e)}")
            return f"❌ Sorry, I couldn't list your tasks. Error: {str(e)}"

    # Command: list completed tasks
    # Matches: "show completed tasks", "list done tasks", "show finished tasks"
    completed_patterns = [
        r'^(?:list|show|view|display|get|see)(?:\s+me)?(?:\s+my)?(?:\s+all)?(?:\s+the)?\s+(?:completed|done|finished)(?:\s+tasks?)?$',
        r'^(?:completed|done|finished)(?:\s+tasks?)?$',
    ]
    for pattern in completed_patterns:
        if re.match(pattern, message_lower, re.IGNORECASE):
            try:
                return await _fetch_and_format_tasks(completed_filter=True, label="Completed tasks")
            except Exception as e:
                logger.error(f"Error listing completed tasks: {str(e)}")
                return f"❌ Sorry, I couldn't list your tasks. Error: {str(e)}"

    # Command: complete task by number
    # Matches: "complete task 1", "mark task 1 as done", "finish task 1", "mark 2 done", "done task 3"
    complete_pattern = r'^(?:complete|finish|done|mark|check\s+off)(?:\s+task)?(?:\s+number)?\s+(\d+|[a-f0-9-]{8,})(?:\s+(?:as\s+)?(?:done|complete|finished))?$'
    match = re.match(complete_pattern, message_lower)
    if match:
        task_ref = match.group(1)
        if task_ref.isdigit():
            try:
                result = await list_tasks(user_id=user_id, db_session=db_session)
                if isinstance(result, dict) and 'tasks' in result:
                    tasks = result['tasks']
                    task_index = int(task_ref) - 1
                    if 0 <= task_index < len(tasks):
                        task_id = tasks[task_index]['task_id']
                        await complete_task(user_id=user_id, task_id=task_id, db_session=db_session)
                        task_title = tasks[task_index].get('title', 'Task')
                        return f"✅ Completed: '{task_title}'\n\nGreat job! Type 'list tasks' to see your remaining tasks."
                    else:
                        return f"❌ Task number {task_ref} not found. Type 'list tasks' to see your tasks."
            except Exception as e:
                logger.error(f"Error completing task: {str(e)}")
                return f"❌ Sorry, I couldn't complete the task. Error: {str(e)}"
        else:
            try:
                await complete_task(user_id=user_id, task_id=task_ref, db_session=db_session)
                return f"✅ Task completed!\n\nType 'list tasks' to see your remaining tasks."
            except Exception as e:
                logger.error(f"Error completing task: {str(e)}")
                return f"❌ Sorry, I couldn't complete the task. Error: {str(e)}"

    # Command: complete task by title (without "mark...as done" phrasing)
    # Matches: "mark buy milk as done", "complete buy milk", "finish buy milk", "i finished buy milk"
    mark_done_pattern = r'^(?:mark|complete|finish|i\s+(?:finished|completed|done))\s+(.+?)(?:\s+(?:as\s+)?(?:done|complete|finished))?$'
    match = re.match(mark_done_pattern, message_lower, re.IGNORECASE)
    if match:
        search_title = match.group(1).strip()
        # Skip if search_title looks like a bare number (handled by the number-based pattern above)
        if not search_title.isdigit():
            try:
                result = await list_tasks(user_id=user_id, db_session=db_session)
                if isinstance(result, dict) and 'tasks' in result:
                    tasks = result['tasks']
                    matched_task = next(
                        (t for t in tasks if search_title in t.get('title', '').lower() and not t.get('completed')),
                        None
                    )
                    if matched_task:
                        await complete_task(user_id=user_id, task_id=matched_task['task_id'], db_session=db_session)
                        return f"✅ Completed: '{matched_task['title']}'\n\nType 'list tasks' to see your remaining tasks."
                    else:
                        return f"❌ No pending task matching '{search_title}' found. Type 'list tasks' to see your tasks."
            except Exception as e:
                logger.error(f"Error completing task by title: {str(e)}")
                return f"❌ Sorry, I couldn't complete the task. Error: {str(e)}"

    # Command: update task by number
    # Matches: "update task 2 to call doctor", "change task 1 to buy groceries", "rename task 3 to meeting"
    update_by_num_pattern = r'^(?:update|change|rename|edit|modify)\s+(?:task\s+)?(\d+)\s+to\s+(.+)$'
    match = re.match(update_by_num_pattern, message_lower, re.IGNORECASE)
    if match:
        task_num = match.group(1)
        new_title = match.group(2).strip()
        try:
            result = await list_tasks(user_id=user_id, db_session=db_session)
            if isinstance(result, dict) and 'tasks' in result:
                tasks = result['tasks']
                task_index = int(task_num) - 1
                if 0 <= task_index < len(tasks):
                    task_id = tasks[task_index]['task_id']
                    old_title = tasks[task_index].get('title', 'Task')
                    await update_task(user_id=user_id, task_id=task_id, title=new_title, db_session=db_session)
                    return f"✅ Updated task {task_num}: '{old_title}' → '{new_title}'"
                else:
                    return f"❌ Task number {task_num} not found. Type 'list tasks' to see your tasks."
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            return f"❌ Sorry, I couldn't update the task. Error: {str(e)}"

    # Command: update task by title
    # Matches: "update buy milk to buy almond milk", "change call doctor to call dentist"
    update_by_title_pattern = r'^(?:update|change|rename|edit|modify)\s+(.+?)\s+to\s+(.+)$'
    match = re.match(update_by_title_pattern, message_lower, re.IGNORECASE)
    if match:
        search_title = match.group(1).strip()
        new_title = match.group(2).strip()
        if not search_title.isdigit():
            try:
                result = await list_tasks(user_id=user_id, db_session=db_session)
                if isinstance(result, dict) and 'tasks' in result:
                    tasks = result['tasks']
                    matched_task = next(
                        (t for t in tasks if search_title in t.get('title', '').lower()),
                        None
                    )
                    if matched_task:
                        old_title = matched_task['title']
                        await update_task(user_id=user_id, task_id=matched_task['task_id'], title=new_title, db_session=db_session)
                        return f"✅ Updated: '{old_title}' → '{new_title}'"
                    else:
                        return f"❌ No task matching '{search_title}' found. Type 'list tasks' to see your tasks."
            except Exception as e:
                logger.error(f"Error updating task by title: {str(e)}")
                return f"❌ Sorry, I couldn't update the task. Error: {str(e)}"

    # Command: delete task by number
    # Matches: "delete task 2", "remove task 3", "delete 1"
    delete_by_num_pattern = r'^(?:delete|remove|cancel|erase)\s+(?:task\s+)?(\d+)$'
    match = re.match(delete_by_num_pattern, message_lower, re.IGNORECASE)
    if match:
        task_num = match.group(1)
        try:
            result = await list_tasks(user_id=user_id, db_session=db_session)
            if isinstance(result, dict) and 'tasks' in result:
                tasks = result['tasks']
                task_index = int(task_num) - 1
                if 0 <= task_index < len(tasks):
                    task_id = tasks[task_index]['task_id']
                    task_title = tasks[task_index].get('title', 'Task')
                    await delete_task(user_id=user_id, task_id=task_id, db_session=db_session)
                    return f"🗑️ Deleted: '{task_title}'"
                else:
                    return f"❌ Task number {task_num} not found. Type 'list tasks' to see your tasks."
        except Exception as e:
            logger.error(f"Error deleting task: {str(e)}")
            return f"❌ Sorry, I couldn't delete the task. Error: {str(e)}"

    # Command: delete task by title
    # Matches: "delete buy milk", "remove call doctor"
    delete_by_title_pattern = r'^(?:delete|remove|cancel|erase)\s+(?:task\s+)?(.+)$'
    match = re.match(delete_by_title_pattern, message_lower, re.IGNORECASE)
    if match:
        search_title = match.group(1).strip()
        if not search_title.isdigit():
            try:
                result = await list_tasks(user_id=user_id, db_session=db_session)
                if isinstance(result, dict) and 'tasks' in result:
                    tasks = result['tasks']
                    matched_task = next(
                        (t for t in tasks if search_title in t.get('title', '').lower()),
                        None
                    )
                    if matched_task:
                        task_title = matched_task['title']
                        await delete_task(user_id=user_id, task_id=matched_task['task_id'], db_session=db_session)
                        return f"🗑️ Deleted: '{task_title}'"
                    else:
                        return f"❌ No task matching '{search_title}' found. Type 'list tasks' to see your tasks."
            except Exception as e:
                logger.error(f"Error deleting task by title: {str(e)}")
                return f"❌ Sorry, I couldn't delete the task. Error: {str(e)}"

    # No command matched
    return None


async def mock_ai_response(message: str, user_id: str = None, db_session: AsyncSession = None) -> str:
    """
    Mock AI response function for fallback when API key is not configured.
    Now includes basic command parsing to handle simple task management commands.
    """
    logger.warning(f"Using mock AI response - no API key configured. Message: {message}")

    # Try to parse as a basic command first
    if user_id and db_session:
        command_result = await parse_basic_command(message, user_id, db_session)
        if command_result:
            return command_result

    # Simple response logic based on the message content
    message_lower = message.lower()

    if any(phrase in message_lower for phrase in ["hello", "hi", "hey", "greetings"]):
        return "Hello! I'm your AI assistant. How can I help you with your tasks today?"
    elif any(phrase in message_lower for phrase in ["help", "what can you do", "assist"]):
        return "I can help you manage your tasks! You can ask me to add, list, complete, update, or delete tasks."
    elif any(phrase in message_lower for phrase in ["thank", "thanks"]):
        return "You're welcome! Let me know if there's anything else I can help with."
    elif any(phrase in message_lower for phrase in ["bye", "goodbye", "see you"]):
        return "Goodbye! Feel free to come back if you need help with your tasks."
    else:
        return (
            f"I couldn't understand: '{message}'\n\n"
            "Try these commands:\n"
            "• **Add:** 'add buy milk' or 'I need to call the doctor'\n"
            "• **List all:** 'list tasks' or 'show my tasks'\n"
            "• **List pending:** 'show pending tasks' or 'what do I need to do today?'\n"
            "• **List done:** 'show completed tasks'\n"
            "• **Complete:** 'complete task 1' or 'complete buy milk' or 'mark buy milk as done'\n"
            "• **Update:** 'update task 2 to call dentist' or 'change buy milk to buy almond milk'\n"
            "• **Delete:** 'delete task 2' or 'remove buy milk'"
        )


async def get_conversation_history(db_session: AsyncSession, conversation_id: str) -> List[Dict[str, str]]:
    """
    Retrieve the conversation history for a given conversation ID.

    CRITICAL FIX: Only include user and assistant messages, exclude tool messages.
    Tool messages cause 400 errors when replayed without proper tool_calls structure.
    """
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc())

    results = await db_session.exec(statement)
    messages = results.all()

    history = []
    for message in messages:
        # CRITICAL: Only include user and assistant messages
        # Tool messages must be excluded to prevent 400 errors
        if message.role in ["user", "assistant"]:
            history.append({
                "role": message.role,
                "content": message.content
            })

    return history


async def call_openai_agent(message: str, user_id: str, conversation_id: str, conversation_history: List[Dict[str, str]], db_session: AsyncSession) -> str:
    """
    Call the OpenAI agent with MCP tools for task management

    PERFORMANCE OPTIMIZATION: Reduced timeout from 60s to 30s to fail faster
    """
    # Create a custom httpx client to avoid proxy parameter issues with OpenAI library
    import httpx
    http_client = httpx.AsyncClient(
        timeout=30.0,  # PERFORMANCE: Reduced from 60s to 30s
        trust_env=False  # Prevent environment proxy settings from interfering
    )

    try:
        # Get the API key for debugging purposes
        api_key = os.getenv("OPENROUTER_API_KEY")
        logger.debug(f"Initializing OpenAI client with API key: {'SET' if api_key else 'NOT SET'}")

        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        # Check for fake/invalid API key formats and return mock response immediately to prevent API calls
        if api_key.startswith("fake-") or "test" in api_key.lower():
            logger.warning("Fake/Invalid API key detected - returning mock response without making API call")
            # Return a mock response that acknowledges the situation and guides the user
            mock_message = f"I'm currently running in demo mode because no valid OpenRouter API key is configured.\n\n"
            mock_message += f"You said: '{message}'\n\n"
            mock_message += f"To enable full AI functionality, please configure a valid OpenRouter API key.\n"
            mock_message += f"Sign up at https://openrouter.ai and add your API key to the OPENROUTER_API_KEY environment variable."
            return mock_message

        # Verify API key format (OpenRouter keys typically start with sk-or-)
        if not api_key.startswith("sk-or-"):
            logger.warning(f"API key format unexpected (doesn't start with 'sk-or-'), attempting to use: {api_key[:10]}...")

        # Prepare additional headers for OpenRouter
        additional_headers = {}
        if os.getenv("HTTP_REFERER"):
            additional_headers["HTTP-Referer"] = os.getenv("HTTP_REFERER")
        if os.getenv("X_TITLE"):
            additional_headers["X-Title"] = os.getenv("X_TITLE")

        client = AsyncOpenAI(
            api_key=api_key,
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            default_headers=additional_headers,
            http_client=http_client
            # NO 'proxies' parameter here - it causes TypeError in newer openai library
        )

        # Prepare the conversation messages
        system_prompt = """You are an AI assistant for a task management application. Help users manage their tasks by understanding their natural language requests and using the appropriate tools.
        - Use add_task to create new tasks when users want to add, remember, or create something
        - Use list_tasks to show users their tasks when they ask to see, show, list, or view tasks
        - Use complete_task to mark tasks as done when users say they finished, completed, or are done with something
        - Use update_task to modify existing tasks when users want to change details
        - Use delete_task to remove tasks when users want to eliminate them

        IMPORTANT: When users refer to tasks by number (e.g., "complete task 1", "delete task 3", "update task 2"), use that number as the task_id. The system will automatically map the number to the actual task ID based on the most recent task list.

        CRITICAL: When a tool returns a message asking for confirmation or additional information (containing words like "confirm", "sure", "provide", "respond with"), you MUST relay that message to the user EXACTLY as provided by the tool. Do NOT say the operation completed - instead, ask the user for the required information or confirmation.

        Be helpful and conversational in your responses."""

        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # PERFORMANCE OPTIMIZATION: Limit conversation history to last 10 messages
        # This reduces token usage and API latency significantly
        limited_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
        messages.extend(limited_history)

        # Add the current user message
        messages.append({"role": "user", "content": message})

        # PERFORMANCE OPTIMIZATION: Reduce max_tokens to 2048 to lower API costs
        # and reduce latency. Most responses don't need 4096 tokens.
        # Call OpenAI with function calling
        response = await client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo"),
            messages=messages,
            tools=get_mcp_tool_schemas(),
            tool_choice="auto",
            max_tokens=2048  # PERFORMANCE: Reduced from default 4096 to 2048
        )

        # Process the response
        response_message = response.choices[0].message

        # Handle tool calls if any
        tool_calls = response_message.tool_calls
        if tool_calls:
            # Add the assistant's message with tool_calls to the conversation
            messages.append({
                "role": "assistant",
                "content": response_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in tool_calls
                ]
            })

            # Process each tool call
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Ensure user_id is passed to all tool calls
                function_args["user_id"] = user_id

                # CRITICAL FIX: Map task numbers to actual task IDs for complete/update/delete operations
                # When AI says "complete task 1", it needs to map "1" to the actual UUID
                # PERFORMANCE OPTIMIZATION: Use cached task list if available
                # EDGE CASE HANDLING: Validate task numbers and provide helpful error messages
                if function_name in ["complete_task", "update_task", "delete_task"]:
                    task_id = function_args.get("task_id", "")

                    # Check if task_id looks like a number (e.g., "1", "2", "3")
                    if task_id and task_id.isdigit():
                        try:
                            task_number = int(task_id)

                            # EDGE CASE: Validate task number is positive
                            if task_number <= 0:
                                raise ValueError(f"Task number must be positive. You entered: {task_number}")

                            # PERFORMANCE: Try to get cached task list first
                            task_list_result = get_cached_task_list(user_id)
                            if not task_list_result:
                                # Cache miss - fetch from database
                                task_list_result = await list_tasks(user_id=user_id, db_session=db_session)
                                if isinstance(task_list_result, dict) and 'tasks' in task_list_result:
                                    set_cached_task_list(user_id, task_list_result)

                            if isinstance(task_list_result, dict) and 'tasks' in task_list_result:
                                tasks = task_list_result['tasks']
                                task_index = task_number - 1  # Convert to 0-based index

                                # EDGE CASE: Provide helpful error for out-of-range task numbers
                                if task_index < 0 or task_index >= len(tasks):
                                    if len(tasks) == 0:
                                        raise ValueError(f"You don't have any tasks yet. Add a task first with 'add [task description]'.")
                                    elif task_number > len(tasks):
                                        raise ValueError(f"Task number {task_number} not found. You only have {len(tasks)} task{'s' if len(tasks) != 1 else ''}. Try 'list tasks' to see your tasks.")
                                    else:
                                        raise ValueError(f"Invalid task number: {task_number}")

                                # Map the number to the actual UUID
                                actual_task_id = tasks[task_index]['task_id']
                                function_args["task_id"] = actual_task_id
                                logger.info(f"Mapped task number {task_number} to task_id {actual_task_id}")
                            else:
                                raise ValueError("Could not retrieve task list. Please try again.")
                        except ValueError as ve:
                            # EDGE CASE: Re-raise ValueError with helpful message
                            logger.warning(f"Task number validation error: {str(ve)}")
                            raise
                        except Exception as mapping_error:
                            logger.error(f"Error mapping task number to ID: {str(mapping_error)}")
                            raise ValueError(f"Error processing task number. Please try 'list tasks' to see your tasks.")

                try:
                    if function_name == "add_task":
                        # EDGE CASE: Validate title is provided
                        title = function_args.get("title", "").strip()
                        if not title:
                            raise ValueError("Please provide a task description. Example: 'add Buy groceries'")

                        result = await add_task(**function_args, db_session=db_session)
                        # PERFORMANCE: Invalidate cache after adding task
                        invalidate_task_cache(user_id)
                        tool_response = str(result)
                    elif function_name == "list_tasks":
                        # PERFORMANCE: Try to use cached task list first
                        cached_result = get_cached_task_list(user_id)
                        if cached_result:
                            result = cached_result
                        else:
                            result = await list_tasks(**function_args, db_session=db_session)
                            if isinstance(result, dict) and 'tasks' in result:
                                set_cached_task_list(user_id, result)
                        tool_response = str(result)
                    elif function_name == "complete_task":
                        # EDGE CASE: Validate task_id is provided
                        task_id = function_args.get("task_id", "").strip()
                        if not task_id:
                            raise ValueError("Please specify which task to complete. Example: 'complete task 1' or 'list tasks' to see your tasks.")

                        result = await complete_task(**function_args, db_session=db_session)
                        # PERFORMANCE: Invalidate cache after completing task
                        invalidate_task_cache(user_id)
                        tool_response = str(result)
                    elif function_name == "update_task":
                        # EDGE CASE: Validate task_id is provided
                        task_id = function_args.get("task_id", "").strip()
                        if not task_id:
                            raise ValueError("Please specify which task to update. Example: 'update task 1 to [new title]' or 'list tasks' to see your tasks.")

                        # CONVERSATION CONTEXT FIX: Check if this is a partial update that needs more info
                        has_title = "title" in function_args and function_args["title"]
                        has_description = "description" in function_args and function_args["description"]

                        # If neither title nor description is provided, we need to ask what to update
                        if not has_title and not has_description:
                            # PERFORMANCE: Try to use cached task list first
                            task_list_result = get_cached_task_list(user_id)
                            if not task_list_result:
                                task_list_result = await list_tasks(user_id=user_id, db_session=db_session)
                                if isinstance(task_list_result, dict) and 'tasks' in task_list_result:
                                    set_cached_task_list(user_id, task_list_result)

                            if isinstance(task_list_result, dict) and 'tasks' in task_list_result:
                                tasks = task_list_result['tasks']
                                task = next((t for t in tasks if t['task_id'] == task_id), None)
                                if task:
                                    task_title = task.get('title', 'Unknown task')
                                    # Set pending operation - we need to know what field to update
                                    # For now, assume description update (most common)
                                    set_pending_operation(conversation_id, "update_description", task_id, task_title, "description")
                                    tool_response = f"Task found: '{task_title}'. What would you like to update? Please provide the new description."
                                else:
                                    # EDGE CASE: Task not found
                                    raise ValueError(f"Task not found. Try 'list tasks' to see your tasks.")
                            else:
                                raise ValueError("Could not retrieve task details. Please try again.")
                        else:
                            # Execute the update normally
                            result = await update_task(**function_args, db_session=db_session)
                            # PERFORMANCE: Invalidate cache after updating task
                            invalidate_task_cache(user_id)
                            tool_response = str(result)
                    elif function_name == "delete_task":
                        # EDGE CASE: Validate task_id is provided
                        task_id = function_args.get("task_id", "").strip()
                        if not task_id:
                            raise ValueError("Please specify which task to delete. Example: 'delete task 1' or 'list tasks' to see your tasks.")

                        # CONVERSATION CONTEXT FIX: Always ask for confirmation before deleting
                        try:
                            logger.info(f"Processing delete_task - task_id: {task_id}, conversation_id: {conversation_id}")

                            # PERFORMANCE: Try to use cached task list first
                            task_list_result = get_cached_task_list(user_id)
                            if not task_list_result:
                                task_list_result = await list_tasks(user_id=user_id, db_session=db_session)
                                if isinstance(task_list_result, dict) and 'tasks' in task_list_result:
                                    set_cached_task_list(user_id, task_list_result)

                            logger.info(f"Got task list result: {type(task_list_result)}")

                            if isinstance(task_list_result, dict) and 'tasks' in task_list_result:
                                tasks = task_list_result['tasks']
                                logger.info(f"Found {len(tasks)} tasks")
                                task = next((t for t in tasks if t['task_id'] == task_id), None)
                                if task:
                                    task_title = task.get('title', 'Unknown task')
                                    logger.info(f"Found task to delete: {task_title}")
                                    # Set pending operation for confirmation
                                    set_pending_operation(conversation_id, "delete", task_id, task_title, "confirmation")
                                    tool_response = f"Found task: '{task_title}'. Are you sure you want to delete this task? Please respond with 'yes' to confirm or 'no' to cancel."
                                    logger.info(f"Set pending operation and created confirmation message")
                                else:
                                    # EDGE CASE: Task not found
                                    logger.warning(f"Task {task_id} not found in task list")
                                    raise ValueError(f"Task not found. Try 'list tasks' to see your tasks.")
                            else:
                                # EDGE CASE: Could not retrieve task list
                                logger.error(f"Could not retrieve task list - result type: {type(task_list_result)}")
                                raise ValueError("Could not retrieve task details. Please try again.")
                        except ValueError as ve:
                            # EDGE CASE: Re-raise ValueError with helpful message
                            logger.warning(f"Delete task validation error: {str(ve)}")
                            raise
                        except Exception as delete_error:
                            logger.error(f"Error in delete_task handler: {str(delete_error)}")
                            logger.error(f"Full traceback: {traceback.format_exc()}")
                            raise ValueError(f"Error processing delete request. Please try again.")
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
                    logger.error(f"Full traceback: {traceback.format_exc()}")
                    messages.append({
                        "role": "tool",
                        "content": f"Error: {str(e)}",
                        "tool_call_id": tool_call.id
                    })

            # CONVERSATION CONTEXT FIX: Check if any tool response contains a confirmation request
            # If so, return it directly to the user without making another AI call
            # This ensures confirmation messages reach the user reliably
            for msg in messages:
                if msg.get("role") == "tool":
                    content = msg.get("content", "")
                    # Check for confirmation keywords
                    confirmation_keywords = ["are you sure", "confirm", "respond with 'yes'", "please respond", "provide"]
                    if any(keyword in content.lower() for keyword in confirmation_keywords):
                        logger.info(f"Detected confirmation request in tool response, returning directly: {content[:100]}")
                        return content

            # Get the final response from the assistant
            final_response = await client.chat.completions.create(
                model=os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo"),
                messages=messages
            )
            return final_response.choices[0].message.content

        else:
            # If no tools were called, return the assistant's response directly
            return response_message.content or "I'm not sure how to help with that."

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error calling OpenAI agent: {error_msg}")
        logger.error(f"Error type: {type(e).__name__}")

        # Log API key info for debugging (without exposing the full key)
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key:
            logger.error(f"API Key is set: True, starts with 'sk-or-': {api_key.startswith('sk-or-')}")

        # Re-raise all errors to let invoke_agent() handle fallback to command parser
        # This ensures the command parser is always tried when AI fails
        raise
    finally:
        # Close the http_client to prevent resource leaks
        try:
            await http_client.aclose()
        except Exception as close_error:
            logger.error(f"Error closing http_client: {close_error}")


async def invoke_agent(
    user_id: str,
    conversation_id: str,
    user_message: str,
    db_session: AsyncSession
) -> str:
    """
    Main function to invoke the AI agent - this routes ALL user messages to the appropriate AI agent
    which will use MCP tools for task management operations
    """
    try:
        # CONVERSATION CONTEXT FIX: Check if there's a pending operation first
        pending_response = await handle_pending_operation(conversation_id, user_message, user_id, db_session)
        if pending_response:
            # A pending operation was handled - return the response
            return pending_response

        # Get conversation history for context (now filtered to exclude tool messages)
        conversation_history = await get_conversation_history(db_session, conversation_id)

        # Try OpenRouter first (to avoid OpenAI quota issues)
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

        # Check if the OpenRouter API key is valid (real OpenRouter keys start with "sk-or-" or "sk-or-v1-")
        if openrouter_api_key and (openrouter_api_key.startswith("sk-or-") or openrouter_api_key.startswith("sk-or-v1-")):
            logger.info(f"Using valid OpenRouter API key for requests - Message: {user_message}")
            try:
                response_text = await call_openai_agent(  # This now uses OpenRouter via base_url
                    message=user_message,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    conversation_history=conversation_history,
                    db_session=db_session
                )
                logger.info(f"OpenRouter API call succeeded - Response length: {len(response_text)}")
            except Exception as e:
                logger.error(f"OpenRouter API call failed for message '{user_message}': {str(e)}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                response_text = await mock_ai_response(user_message, user_id, db_session)
        elif openrouter_api_key and openrouter_api_key.startswith("fake-"):
            logger.warning("Fake API key detected, using mock response for testing")
            response_text = await mock_ai_response(user_message, user_id, db_session)
        elif openrouter_api_key:
            # Key exists but doesn't start with expected prefixes, might be another provider or invalid format
            logger.warning(f"API key detected but format unexpected (doesn't start with 'sk-or-'), attempting to use: {openrouter_api_key[:10]}...")
            try:
                response_text = await call_openai_agent(
                    message=user_message,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    conversation_history=conversation_history,
                    db_session=db_session
                )
            except Exception as e:
                logger.error(f"OpenRouter API call failed with provided key: {str(e)}")
                # Fallback to mock response if OpenRouter call fails
                response_text = await mock_ai_response(user_message, user_id, db_session)
        else:
            # Fallback to OpenAI if OpenRouter not configured
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key and openai_api_key.startswith("sk-"):  # Standard OpenAI key format
                logger.info("Using OpenAI API key for requests")
                try:
                    response_text = await call_openai_agent(
                        message=user_message,
                        user_id=user_id,
                        conversation_id=conversation_id,
                        conversation_history=conversation_history,
                        db_session=db_session
                    )
                except Exception as e:
                    logger.error(f"OpenAI API call failed: {str(e)}")
                    response_text = await mock_ai_response(user_message, user_id, db_session)
            elif openai_api_key and openai_api_key.startswith("fake-"):
                logger.warning("Fake OpenAI API key detected, using mock response")
                response_text = await mock_ai_response(user_message, user_id, db_session)
            elif openai_api_key:
                logger.warning(f"OpenAI key detected but format unexpected, attempting to use: {openai_api_key[:10]}...")
                try:
                    response_text = await call_openai_agent(
                        message=user_message,
                        user_id=user_id,
                        conversation_id=conversation_id,
                        conversation_history=conversation_history,
                        db_session=db_session
                    )
                except Exception as e:
                    logger.error(f"OpenAI API call failed: {str(e)}")
                    response_text = await mock_ai_response(user_message, user_id, db_session)
            else:
                # If no API keys are configured, return a mock response
                logger.warning("No valid API keys configured, using mock response")
                response_text = await mock_ai_response(user_message, user_id, db_session)

        return response_text

    except Exception as e:
        logger.error(f"Error in invoke_agent: {str(e)}")
        raise
