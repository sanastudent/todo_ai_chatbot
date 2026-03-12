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
                "description": "Permanently delete a task. Call this when the user wants to remove or delete a task.",
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


async def call_openai_agent(message: str, user_id: str, conversation_history: List[Dict[str, str]] = None) -> str:
    """
    Call the OpenAI agent with MCP tools for function calling
    """
    if not openai_api_key:
        logger.warning("OpenAI API key not set, falling back to mock response")
        return await mock_ai_response(message)

    # Initialize the OpenAI client only when needed
    # Avoid passing 'proxies' parameter to prevent AsyncClient error
    import openai
    import httpx

    # Create a transport with explicit proxy settings disabled
    transport = httpx.HTTPTransport(trust_env=False)

    # Create a custom httpx client with the safe transport and explicit proxy avoidance
    http_client = httpx.AsyncClient(
        timeout=60.0,
        transport=transport,
        trust_env=False  # Explicitly disable environment proxy settings
    )

    client_kwargs = {
        "api_key": openai_api_key,
        "http_client": http_client
    }

    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        client_kwargs["base_url"] = base_url

    async_client = AsyncOpenAI(**client_kwargs)

    # Prepare the conversation messages
    messages = []

    # Add system message to instruct the agent on task management
    messages.append({
        "role": "system",
        "content": "You are an AI assistant for a task management application. Help users manage their tasks by calling appropriate tools. "
                   "Recognize user intent and call the appropriate MCP tool: "
                   "1. add_task: for requests to add/create/new tasks ('add', 'create', 'remember to', 'need to', 'todo', etc.) "
                   "2. list_tasks: for requests to see/view/show/list tasks ('show', 'list', 'view', 'see', 'what', 'display', etc.) "
                   "3. complete_task: for requests to finish/done/complete tasks ('complete', 'finish', 'done', 'mark as done', 'completed', 'cross off', etc.) "
                   "4. update_task: for requests to change/edit/modify tasks ('update', 'change', 'modify', 'edit', 'rename', 'adjust', etc.) "
                   "5. delete_task: for requests to remove/delete/cancel tasks ('delete', 'remove', 'cancel', 'erase', 'get rid of', etc.) "
                   "Always call the appropriate tool based on user intent. If you cannot determine the appropriate action, ask the user for clarification."
    })

    # Add conversation history if available
    if conversation_history:
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # Add the current user message
    messages.append({
        "role": "user",
        "content": message
    })

    try:
        # Call OpenAI with function calling
        response = await async_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=messages,
            tools=get_mcp_tool_schemas(),
            tool_choice="auto"
        )

        response_message = response.choices[0].message

        # Check if the model wanted to call a function
        tool_calls = response_message.tool_calls

        if tool_calls:
            # Process tool calls
            tool_responses = []

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Call the appropriate MCP tool based on the function name
                if function_name == "add_task":
                    result = await add_task(
                        user_id=function_args["user_id"],
                        title=function_args.get("title"),
                        description=function_args.get("description"),
                        priority=function_args.get("priority"),
                        tags=function_args.get("tags"),
                        db_session=None  # Will be created internally
                    )
                elif function_name == "list_tasks":
                    result = await list_tasks(
                        user_id=function_args["user_id"],
                        completed=function_args.get("completed"),
                        priority=function_args.get("priority"),
                        tags=function_args.get("tags"),
                        search_term=function_args.get("search_term"),
                        date_from=function_args.get("date_from"),
                        date_to=function_args.get("date_to"),
                        sort_by=function_args.get("sort_by"),
                        sort_order=function_args.get("sort_order"),
                        limit=function_args.get("limit", 50),
                        offset=function_args.get("offset", 0),
                        db_session=None  # Will be created internally
                    )
                elif function_name == "complete_task":
                    result = await complete_task(
                        user_id=function_args["user_id"],
                        task_id=function_args["task_id"],
                        db_session=None  # Will be created internally
                    )
                elif function_name == "update_task":
                    result = await update_task(
                        user_id=function_args["user_id"],
                        task_id=function_args["task_id"],
                        title=function_args.get("title"),
                        description=function_args.get("description"),
                        priority=function_args.get("priority"),
                        tags=function_args.get("tags"),
                        db_session=None  # Will be created internally
                    )
                elif function_name == "delete_task":
                    result = await delete_task(
                        user_id=function_args["user_id"],
                        task_id=function_args["task_id"],
                        db_session=None  # Will be created internally
                    )
                else:
                    result = {"error": f"Unknown function: {function_name}"}

                tool_responses.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result)
                })

            # Call the model again with the tool responses to get the final response
            messages.extend(tool_responses)

            final_response = await async_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=messages
            )

            return final_response.choices[0].message.content

        else:
            # If no tool was called, return the model's response directly
            return response_message.content

    except Exception as e:
        logger.error(f"Error calling OpenAI agent: {str(e)}", exc_info=True)
        logger.error(f"OpenAI API key configured: {bool(openai_api_key)}")
        logger.error(f"Message that failed: {message}")
        # Fallback to mock response if OpenAI call fails
        return await mock_ai_response(message)


async def call_openrouter_agent(message: str, user_id: str, conversation_history: List[Dict[str, str]] = None) -> str:
    """
    Call the OpenRouter agent with enhanced prompting for better task management understanding
    """
    # Prepare the conversation messages
    messages = []

    # Add system message to instruct the agent on task management
    messages.append({
        "role": "system",
        "content": "You are an advanced AI assistant for a task management application. Help users manage their tasks by understanding their natural language requests. "
                   "Recognize user intent and call the appropriate operation: "
                   "1. add_task: for requests to add/create/new tasks ('add', 'create', 'remember to', 'need to', 'todo', etc.) "
                   "2. list_tasks: for requests to see/view/show/list tasks ('show', 'list', 'view', 'see', 'what', 'display', etc.) "
                   "3. complete_task: for requests to finish/done/complete tasks ('complete', 'finish', 'done', 'mark as done', 'completed', 'cross off', etc.) "
                   "4. update_task: for requests to change/edit/modify tasks ('update', 'change', 'modify', 'edit', 'rename', 'adjust', etc.) "
                   "5. delete_task: for requests to remove/delete/cancel tasks ('delete', 'remove', 'cancel', 'erase', 'get rid of', etc.) "
                   "You are connected to a task management system that can perform these operations. "
                   "Examples: 'add buy groceries' -> add a task, 'show tasks' -> list tasks, 'complete task 1' -> complete a task, etc."
    })

    # Add conversation history if available
    if conversation_history:
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # Add the current user message
    messages.append({
        "role": "user",
        "content": message
    })

    try:
        # Enhanced prompt to guide the AI in understanding task management commands
        enhanced_message = f"""
        You are an AI assistant for a task management application. You need to understand and respond to various commands related to task management.

        Available capabilities:
        1. add_task: To add a new task - triggered by phrases like "add", "create", "remember to", "need to", "todo", etc.
        2. list_tasks: To list existing tasks - triggered by phrases like "show", "list", "view", "see", "what", "display", etc.
        3. complete_task: To mark a task as completed - triggered by phrases like "complete", "finish", "done", "mark as done", "completed", "cross off", etc.
        4. update_task: To update task details - triggered by phrases like "update", "change", "modify", "edit", "rename", "adjust", etc.
        5. delete_task: To delete a task - triggered by phrases like "delete", "remove", "cancel", "erase", "get rid of", etc.

        When the user says:
        - Commands to add tasks: "add buy groceries", "create a meeting with John", "remind me to call mom", "need to water plants"
        - Commands to list tasks: "show my tasks", "what do I have to do", "list tasks", "view todos"
        - Commands to complete tasks: "complete task 1", "finish the report", "mark task as done", "done with shopping", "cross off task 3"
        - Commands to update tasks: "change task 1 title to 'new title'", "update the deadline", "edit meeting time", "rename task 2"
        - Commands to delete tasks: "delete task 1", "remove the appointment", "cancel the reminder", "get rid of task 5"

        User message: {message}

        Please respond appropriately to the user's request by understanding their intent and formulating an appropriate response.
        """

        api_key = os.getenv("OPENROUTER_API_KEY")
        model = os.getenv("OPENROUTER_MODEL", "google/gemini-pro")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": enhanced_message}
            ],
            "temperature": 0.7
        }

        # Create httpx client with explicit proxy=None to avoid any proxy configuration
        async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                raise Exception(f"API request failed with status {response.status_code}")

            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Error calling OpenRouter agent: {str(e)}", exc_info=True)
        logger.error(f"OpenRouter API key configured: {bool(api_key)}")
        logger.error(f"OpenRouter model: {model}")
        logger.error(f"Message that failed: {message}")
        # Fallback to mock response if OpenRouter call fails
        return await mock_ai_response(message)


async def mock_ai_response(message: str) -> str:
    """
    Mock AI response function for fallback when API key is not configured
    """
    logger.warning(f"Using mock AI response - no API key configured. Message: {message}")

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
            f"I couldn't understand your request: '{message}'\n\n"
            "⚠️ Note: AI natural language processing is not available (no API key configured).\n\n"
            "Try using specific commands like:\n"
            "• 'add [task]' - Add a new task\n"
            "• 'list tasks' or 'show my tasks' - View all tasks\n"
            "• 'complete task [number]' - Mark a task as done\n"
            "• 'delete task [number]' - Remove a task\n"
            "• 'update task [number] to [new title]' - Change a task"
        )


async def get_conversation_history(db_session: AsyncSession, conversation_id: str) -> List[Dict[str, str]]:
    """
    Load conversation history for the agent
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


async def invoke_agent(
    user_id: str,
    conversation_id: str,
    user_message: str,
    db_session: AsyncSession
) -> str:
    """
    Invoke the AI agent with pattern matching for natural language commands
    """
    try:
        # REMOVE SURROUNDING QUOTES
        if user_message.startswith('"') and user_message.endswith('"') and len(user_message) > 1:
            user_message = user_message[1:-1]  # Remove first and last character
        if user_message.startswith("'") and user_message.endswith("'") and len(user_message) > 1:
            user_message = user_message[1:-1]

        # DEBUG: Check if function is being called
        print(f"DEBUG: invoke_agent called with message: '{user_message}'")
        print(f"DEBUG: stripped and lowercased: '{user_message.strip().lower()}'")

        # Search for tasks by title (helper function for title-based operations)
        async def find_task_by_title(title_query: str) -> Optional[Dict[str, Any]]:
            """Find a task by its title"""
            try:
                # Get all tasks for the user
                all_tasks_result = await list_tasks(
                    user_id=user_id,
                    completed=None,  # Get all tasks regardless of completion status
                    db_session=db_session
                )

                if "tasks" in all_tasks_result:
                    tasks = all_tasks_result["tasks"]

                    # Search for tasks with matching title (case-insensitive partial match)
                    for task in tasks:
                        if title_query.lower() in task.get('title', '').lower():
                            return task

                return None
            except Exception as e:
                logger.error(f"Error finding task by title '{title_query}': {str(e)}")
                return None

        # Helper functions for MCP tool operations
        async def add_task_handler(title):
            result = await add_task(
                user_id=user_id,
                title=title.strip(),
                description=None,
                priority=None,
                tags=None,
                db_session=db_session
            )
            return f"I've added '{title.strip()}' to your tasks. Task ID: {result['task_id']}"

        async def list_pending_tasks_handler():
            result = await list_tasks(
                user_id=user_id,
                completed=False,  # Only pending tasks
                db_session=db_session
            )
            if "tasks" in result and result["tasks"]:
                pending_tasks = [task for task in result["tasks"] if not task.get("completed", False)]
                if pending_tasks:
                    task_list = []
                    for i, task in enumerate(pending_tasks, 1):
                        task_entry = f"{i}. {task['title']}"
                        if task.get("priority"):
                            task_entry = f"[{task['priority'].upper()}] {task_entry}"
                        task_list.append(task_entry)
                    return f"Here are your pending tasks:\n" + "\n".join(task_list)
                else:
                    return "You have no pending tasks."
            else:
                return "You have no pending tasks."

        async def list_completed_tasks_handler():
            result = await list_tasks(
                user_id=user_id,
                completed=True,  # Only completed tasks
                db_session=db_session
            )
            if "tasks" in result and result["tasks"]:
                completed_tasks = [task for task in result["tasks"] if task.get("completed", False)]
                if completed_tasks:
                    task_list = []
                    for i, task in enumerate(completed_tasks, 1):
                        task_entry = f"{i}. {task['title']}"
                        task_list.append(task_entry)
                    return f"Here are your completed tasks:\n" + "\n".join(task_list)
                else:
                    return "You haven't completed any tasks yet."
            else:
                return "You haven't completed any tasks yet."

        async def list_all_tasks_handler():
            result = await list_tasks(
                user_id=user_id,
                completed=None,  # All tasks
                db_session=db_session
            )
            if "tasks" in result and result["tasks"]:
                task_list = []
                for i, task in enumerate(result["tasks"], 1):
                    status = "✓" if task.get("completed", False) else "○"
                    task_entry = f"{i}. [{status}] {task['title']}"
                    if task.get("priority"):
                        task_entry = f"[{task['priority'].upper()}] {task_entry}"
                    task_list.append(task_entry)
                return f"Here are your tasks:\n" + "\n".join(task_list)
            else:
                return "You have no tasks yet."

        async def complete_task_by_title(title_query):
            task = await find_task_by_title(title_query)
            if task:
                result = await complete_task(
                    user_id=user_id,
                    task_id=task["task_id"],
                    db_session=db_session
                )
                return f"I've marked '{task['title']}' as completed."
            else:
                return f"I couldn't find a task containing '{title_query}'. Could you be more specific?"

        async def delete_task_by_title(title_query):
            task = await find_task_by_title(title_query)
            if task:
                result = await delete_task(
                    user_id=user_id,
                    task_id=task["task_id"],
                    db_session=db_session
                )
                return f"I've deleted the task '{task['title']}'."
            else:
                return f"I couldn't find a task containing '{title_query}'. Could you be more specific?"

        async def update_task_title(old_title, new_title):
            task = await find_task_by_title(old_title)
            if task:
                result = await update_task(
                    user_id=user_id,
                    task_id=task["task_id"],
                    title=new_title,
                    db_session=db_session
                )
                return f"I've changed the task '{task['title']}' to '{new_title}'."
            else:
                return f"I couldn't find a task containing '{old_title}'. Could you be more specific?"

        async def update_task_description(title_query, new_description):
            task = await find_task_by_title(title_query)
            if task:
                result = await update_task(
                    user_id=user_id,
                    task_id=task["task_id"],
                    description=new_description,
                    db_session=db_session
                )
                return f"I've updated the task '{task['title']}' with the note: '{new_description}'."
            else:
                return f"I couldn't find a task containing '{title_query}'. Could you be more specific?"

        async def complete_task_by_id(task_num):
            # Get all tasks to map by position
            all_tasks_result = await list_tasks(user_id=user_id, completed=None, db_session=db_session)
            all_tasks = all_tasks_result["tasks"]

            # Convert the number to an index (1-based to 0-based)
            task_idx = int(task_num) - 1

            if 0 <= task_idx < len(all_tasks):
                task_to_update_obj = all_tasks[task_idx]
                task_id = task_to_update_obj["task_id"]

                result = await complete_task(
                    user_id=user_id,
                    task_id=task_id,
                    db_session=db_session
                )
                return f"I've marked task '{task_to_update_obj['title']}' as completed."
            else:
                return f"Could not find task number {task_num}. Please specify a number between 1 and {len(all_tasks)}."

        async def delete_task_by_id(task_num):
            # Get all tasks to map by position
            all_tasks_result = await list_tasks(user_id=user_id, completed=None, db_session=db_session)
            all_tasks = all_tasks_result["tasks"]

            # Convert the number to an index (1-based to 0-based)
            task_idx = int(task_num) - 1

            if 0 <= task_idx < len(all_tasks):
                task_to_delete_obj = all_tasks[task_idx]
                task_id = task_to_delete_obj["task_id"]

                result = await delete_task(
                    user_id=user_id,
                    task_id=task_id,
                    db_session=db_session
                )
                return f"I've deleted task '{task_to_delete_obj['title']}'."
            else:
                return f"Could not find task number {task_num}. Please specify a number between 1 and {len(all_tasks)}."

        async def update_task_by_id(task_num, new_title):
            # Get all tasks to map by position
            all_tasks_result = await list_tasks(user_id=user_id, completed=None, db_session=db_session)
            all_tasks = all_tasks_result["tasks"]

            # Convert the number to an index (1-based to 0-based)
            task_idx = int(task_num) - 1

            if 0 <= task_idx < len(all_tasks):
                task_to_update_obj = all_tasks[task_idx]
                task_id = task_to_update_obj["task_id"]

                result = await update_task(
                    user_id=user_id,
                    task_id=task_id,
                    title=new_title,
                    db_session=db_session
                )
                return f"I've updated task '{task_to_update_obj['title']}' title to '{new_title}'."
            else:
                return f"Could not find task number {task_num}. Please specify a number between 1 and {len(all_tasks)}."

        # Define patterns in order of priority
        patterns = [
            # NEW: Additional add_task patterns
            (r'^i want to (.+?)(?:[.!?]*\s*)$', lambda m: add_task_handler(m.group(1))),
            (r'^i would like to (.+?)(?:[.!?]*\s*)$', lambda m: add_task_handler(m.group(1))),
            (r'^please add (.+?)(?:[.!?]*\s*)$', lambda m: add_task_handler(m.group(1))),
            (r'^can you add (.+?)(?:[.!?]*\s*)$', lambda m: add_task_handler(m.group(1))),
            (r'^i have to (.+?)(?:[.!?]*\s*)$', lambda m: add_task_handler(m.group(1))),

            # 1. Original add_task patterns
            (r'^remind me to (.+?)(?:[.!?]*\s*)$', lambda m: add_task_handler(m.group(1))),
            (r'^i need to (.+?)(?:[.!?]*\s*)$', lambda m: add_task_handler(m.group(1))),
            (r'^add task to (.+?)(?:[.!?]*\s*)$', lambda m: add_task_handler(m.group(1))),
            (r'^add a task to (.+?)(?:[.!?]*\s*)$', lambda m: add_task_handler(m.group(1))),
            (r'^add (.+?)(?:[.!?]*\s*)$', lambda m: add_task_handler(m.group(1))),  # Most generic add pattern

            # NEW: Additional list_tasks patterns
            (r'^show all tasks[.!?]*\s*$', lambda m: list_all_tasks_handler()),
            (r'^what tasks do i have[.!?]*\s*$', lambda m: list_all_tasks_handler()),
            (r'^(?:show|list)(?: my)? tasks[.!?]*\s*$', lambda m: list_all_tasks_handler()),  # Matches "show tasks", "list tasks", "show my tasks", "list my tasks"
            (r'^(?:show|list) (?:me )?(?:my )?tasks[.!?]*\s*$', lambda m: list_all_tasks_handler()),  # More flexible matching

            # 2. Original list_tasks patterns
            (r'^show (?:me )?my pending tasks[.!?]*\s*$', lambda m: list_pending_tasks_handler()),
            (r'^what have i completed[.!?]*\s*$', lambda m: list_completed_tasks_handler()),
            (r'^what\'s on my list[.!?]*\s*$', lambda m: list_all_tasks_handler()),
            (r'^show me my tasks[.!?]*\s*$', lambda m: list_all_tasks_handler()),

            # NEW: Additional complete_task patterns
            (r'^task (\d+) is done[.!?]*\s*$', lambda m: complete_task_by_id(m.group(1))),
            (r'^complete(?: my)? task (\d+)(?: please)?[.!?]*\s*$', lambda m: complete_task_by_id(m.group(1))),  # Matches "complete my task 1", "complete task 1 please"
            (r'^finish(?: my)? task (\d+)(?: please)?[.!?]*\s*$', lambda m: complete_task_by_id(m.group(1))),  # Matches "finish my task 2"
            (r'^mark(?: my)? task (\d+) (?:as )?done[.!?]*\s*$', lambda m: complete_task_by_id(m.group(1))),  # Matches "mark my task 1 done", "mark task 1 as done"

            # 3. Original complete_task patterns
            (r'^mark (.+?) as done[.!?]*\s*$', lambda m: complete_task_by_title(m.group(1))),
            (r'^complete (.+?) task[.!?]*\s*$', lambda m: complete_task_by_title(m.group(1))),
            (r'^finish (.+?) task[.!?]*\s*$', lambda m: complete_task_by_title(m.group(1))),

            # NEW: Additional delete_task patterns
            (r'^remove task (\d+)[.!?]*\s*$', lambda m: delete_task_by_id(m.group(1))),
            (r'^delete(?: my)? task (\d+)(?: please)?[.!?]*\s*$', lambda m: delete_task_by_id(m.group(1))),  # Matches "delete my task 3", "delete task 3 please"
            (r'^remove(?: my)? task (\d+)(?: please)?[.!?]*\s*$', lambda m: delete_task_by_id(m.group(1))),  # Matches "remove my task 1"
            (r'^cancel(?: my)? task (\d+)(?: please)?[.!?]*\s*$', lambda m: delete_task_by_id(m.group(1))),  # Matches "cancel my task 2"

            # 4. Original delete_task patterns
            (r'^delete (.+?) task[.!?]*\s*$', lambda m: delete_task_by_title(m.group(1))),
            (r'^remove (.+?) task[.!?]*\s*$', lambda m: delete_task_by_title(m.group(1))),
            (r'^cancel (.+?) task[.!?]*\s*$', lambda m: delete_task_by_title(m.group(1))),

            # 5. update_task patterns
            (r'^change (.+?) to (.+?)(?:[.!?]*\s*)$', lambda m: update_task_title(m.group(1), m.group(2))),
            (r'^rename (.+?) to (.+?)(?:[.!?]*\s*)$', lambda m: update_task_title(m.group(1), m.group(2))),
            (r'^update (.+?) with note: (.+?)(?:[.!?]*\s*)$', lambda m: update_task_description(m.group(1), m.group(2))),

            # Existing working number-based patterns (KEEP THESE)
            (r'^complete task (\d+)[.!?]*\s*$', lambda m: complete_task_by_id(m.group(1))),
            (r'^delete task (\d+)[.!?]*\s*$', lambda m: delete_task_by_id(m.group(1))),
            (r'^update task (\d+) to (.+?)(?:[.!?]*\s*)$', lambda m: update_task_by_id(m.group(1), m.group(2))),
        ]

        # Process patterns in order
        # Strip leading and trailing quotes before pattern matching
        processed_message = user_message.strip().lower()
        if processed_message.startswith('"') and processed_message.endswith('"') and len(processed_message) > 1:
            processed_message = processed_message[1:-1]  # Remove leading and trailing quotes

        for pattern, handler in patterns:
            match = re.search(pattern, processed_message)
            if match:
                try:
                    result = handler(match)
                    # If result is a coroutine, await it
                    if hasattr(result, '__await__'):
                        result = await result
                    return result if isinstance(result, str) else str(result)
                except Exception as e:
                    logger.error(f"Error processing pattern '{pattern}' with message '{user_message}': {str(e)}")
                    continue  # Continue to next pattern

        # If no patterns matched, fall back to AI agent
        # Get conversation history for context
        conversation_history = await get_conversation_history(db_session, conversation_id)

        # Try OpenAI agent first (if API key is configured)
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            response_text = await call_openai_agent(
                message=user_message,
                user_id=user_id,
                conversation_history=conversation_history
            )
        else:
            # Fallback to OpenRouter agent
            openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
            if openrouter_api_key:
                response_text = await call_openrouter_agent(
                    message=user_message,
                    user_id=user_id,
                    conversation_history=conversation_history
                )
            else:
                # If no API keys are configured, use mock response
                response_text = await mock_ai_response(user_message)

        # Strip leading and trailing quotes for individual pattern matching
        processed_message_for_individual_patterns = user_message.strip()
        if processed_message_for_individual_patterns.startswith('"') and processed_message_for_individual_patterns.endswith('"') and len(processed_message_for_individual_patterns) > 1:
            processed_message_for_individual_patterns = processed_message_for_individual_patterns[1:-1]  # Remove leading and trailing quotes

        # Pattern: update task (\d+) title to (.+) → update_task
        update_title_match = re.search(r'^update task (\d+) title to (.+)$', processed_message_for_individual_patterns)
        if update_title_match:
            task_num = int(update_title_match.group(1))
            new_title = update_title_match.group(2).strip()
            print(f"[DEBUG] Calling update_task: task {task_num} title to '{new_title}'")

            # Get all tasks to map by position
            all_tasks_result = await list_tasks(user_id=user_id, completed=None, db_session=db_session)
            all_tasks = all_tasks_result["tasks"]

            # Convert the number to an index (1-based to 0-based)
            task_idx = task_num - 1

            if 0 <= task_idx < len(all_tasks):
                task_to_update_obj = all_tasks[task_idx]
                task_id = task_to_update_obj["task_id"]

                # Call the update_task function directly with the new title
                result = await update_task(
                    user_id=user_id,
                    task_id=task_id,
                    title=new_title,
                    db_session=db_session
                )
                return f"I've updated task '{task_to_update_obj['title']}' title to '{new_title}'."
            else:
                return f"Could not find task number {task_num}. Please specify a number between 1 and {len(all_tasks)}."

        # Pattern: change task (\d+) to (high|medium|low) priority → update_task
        change_priority_match = re.search(r'^change task (\d+) to (high|medium|low) priority$', processed_message_for_individual_patterns, re.IGNORECASE)
        if change_priority_match:
            task_num = int(change_priority_match.group(1))
            new_priority = change_priority_match.group(2).strip()

            # Get all tasks to map by position
            all_tasks_result = await list_tasks(user_id=user_id, completed=None, db_session=db_session)
            all_tasks = all_tasks_result["tasks"]

            # Convert the number to an index (1-based to 0-based)
            task_idx = task_num - 1

            if 0 <= task_idx < len(all_tasks):
                task_to_update_obj = all_tasks[task_idx]
                task_id = task_to_update_obj["task_id"]

                # Call the update_task function directly with the new priority
                result = await update_task(
                    user_id=user_id,
                    task_id=task_id,
                    priority=new_priority,
                    db_session=db_session
                )
                return f"I've updated task '{task_to_update_obj['title']}' priority to {new_priority}."
            else:
                return f"Could not find task number {task_num}. Please specify a number between 1 and {len(all_tasks)}."

        # Pattern: mark task (\d+) as (high|medium|low) priority → update_task
        mark_priority_match = re.search(r'^mark task (\d+) as (high|medium|low) priority$', processed_message_for_individual_patterns, re.IGNORECASE)
        if mark_priority_match:
            task_num = int(mark_priority_match.group(1))
            new_priority = mark_priority_match.group(2).strip()

            # Get all tasks to map by position
            all_tasks_result = await list_tasks(user_id=user_id, completed=None, db_session=db_session)
            all_tasks = all_tasks_result["tasks"]

            # Convert the number to an index (1-based to 0-based)
            task_idx = task_num - 1

            if 0 <= task_idx < len(all_tasks):
                task_to_update_obj = all_tasks[task_idx]
                task_id = task_to_update_obj["task_id"]

                # Call the update_task function directly with the new priority
                result = await update_task(
                    user_id=user_id,
                    task_id=task_id,
                    priority=new_priority,
                    db_session=db_session
                )
                return f"I've updated task '{task_to_update_obj['title']}' priority to {new_priority}."
            else:
                return f"Could not find task number {task_num}. Please specify a number between 1 and {len(all_tasks)}."

        # Pattern: delete task (\d+) → delete_task
        delete_match = re.search(r'^delete task (\d+)$', processed_message_for_individual_patterns)

        # Handle typo: "delete taks" instead of "delete task"
        delete_typo_match = re.search(r'^delete.*taks?\s*(\d+)$', processed_message_for_individual_patterns)
        if delete_typo_match:
            task_num = int(delete_typo_match.group(1))

            # Get all tasks to map by position
            all_tasks_result = await list_tasks(user_id=user_id, completed=None, db_session=db_session)
            all_tasks = all_tasks_result["tasks"]

            # Convert the number to an index (1-based to 0-based)
            task_idx = task_num - 1

            # Add additional safety check to ensure we're not dealing with negative indices
            if task_num <= 0:
                return f"Invalid task number {task_num}. Task numbers must be positive integers."

            if 0 <= task_idx < len(all_tasks):
                task_to_delete_obj = all_tasks[task_idx]
                task_id = task_to_delete_obj["task_id"]

                # Call the delete_task function directly
                result = await delete_task(
                    user_id=user_id,
                    task_id=task_id,
                    db_session=db_session
                )
                return f"I've deleted task '{task_to_delete_obj['title']}'."
            else:
                return f"Could not find task number {task_num}. Please specify a number between 1 and {len(all_tasks)}."
        elif delete_match:
            task_num = int(delete_match.group(1))
            print(f"[DEBUG] Calling delete_task for task {task_num}")

            # Get all tasks to map by position
            all_tasks_result = await list_tasks(user_id=user_id, completed=None, db_session=db_session)
            all_tasks = all_tasks_result["tasks"]

            # Convert the number to an index (1-based to 0-based)
            task_idx = task_num - 1

            # Add additional safety check to ensure we're not dealing with negative indices
            if task_num <= 0:
                return f"Invalid task number {task_num}. Task numbers must be positive integers."

            if 0 <= task_idx < len(all_tasks):
                task_to_delete_obj = all_tasks[task_idx]
                task_id = task_to_delete_obj["task_id"]

                # Call the delete_task function directly
                result = await delete_task(
                    user_id=user_id,
                    task_id=task_id,
                    db_session=db_session
                )
                return f"I've deleted task '{task_to_delete_obj['title']}'."
            else:
                return f"Could not find task number {task_num}. Please specify a number between 1 and {len(all_tasks)}."

        # INTERMEDIATE PATTERNS (MUST WORK):

        # NEW: Pattern for "find [query] tasks" → search_tasks
        find_tasks_match = re.search(r'^find (.+) tasks$', processed_message_for_individual_patterns, re.IGNORECASE)
        if find_tasks_match:
            query = find_tasks_match.group(1).strip()

            # Avoid triggering on common categories that should be handled differently
            common_categories = ['work', 'personal', 'shopping', 'urgent', 'home', 'high', 'medium', 'low']
            if query.lower() in common_categories:
                pass  # Let other handlers manage these
            else:
                try:
                    search_result = await search_tasks(
                        user_id=user_id,
                        query=query,
                        search_in=['title', 'description', 'tags'],
                        db_session=db_session
                    )

                    tasks = search_result["tasks"]

                    if not tasks:
                        return f"No tasks found matching '{query}'."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "HIGH "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "MED "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "LOW "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"[DONE] {task_entry}"
                        else:
                            task_entry = f"[TODO] {task_entry}"
                        task_list.append(task_entry)

                    return f"Found {len(tasks)} tasks matching '{query}':\n" + "\n".join(task_list)
                except Exception as e:
                    logger.error(f"Error searching tasks: {str(e)}")
                    return "Sorry, I couldn't search your tasks. Please try again."

        # NEW: Pattern for "show [priority] tasks" → filter_tasks
        show_priority_tasks_match = re.search(r'^show (.+?) tasks$', processed_message_for_individual_patterns)
        if show_priority_tasks_match and not re.search(r'^show tasks with (.+) tag$', processed_message_for_individual_patterns):  # Avoid conflicting with existing pattern
            potential_priority = show_priority_tasks_match.group(1).strip()

            # Check if it's a priority filter
            common_priorities = ['high', 'medium', 'low']

            if potential_priority.lower() in common_priorities:
                priority = potential_priority.lower()

                try:
                    # Use filter_tasks function with priority
                    filter_result = await filter_tasks(
                        user_id=user_id,
                        priority=[priority],  # Note: filter_tasks expects a list
                        db_session=db_session
                    )

                    tasks = filter_result["tasks"]

                    if not tasks:
                        return f"No {priority} priority tasks found."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "HIGH "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "MED "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "LOW "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"[DONE] {task_entry}"
                        else:
                            task_entry = f"[TODO] {task_entry}"
                        task_list.append(task_entry)

                    return f"Here are your {priority} priority tasks ({len(tasks)} total):\n" + "\n".join(task_list)
                except Exception as e:
                    logger.error(f"Error filtering tasks by priority: {str(e)}")
                    return "Sorry, I couldn't filter your tasks by priority. Please try again."

        # NEW: Pattern for "show tasks by [priority]" → filter_tasks
        show_tasks_by_priority_match = re.search(r'^show tasks by (.+?)$', processed_message_for_individual_patterns)
        if show_tasks_by_priority_match:
            potential_priority = show_tasks_by_priority_match.group(1).strip()

            # Check if it's a priority filter
            common_priorities = ['high', 'medium', 'low']

            if potential_priority.lower() in common_priorities:
                priority = potential_priority.lower()

                try:
                    # Use filter_tasks function with priority
                    filter_result = await filter_tasks(
                        user_id=user_id,
                        priority=[priority],  # Note: filter_tasks expects a list
                        db_session=db_session
                    )

                    tasks = filter_result["tasks"]

                    if not tasks:
                        return f"No {priority} priority tasks found."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "HIGH "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "MED "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "LOW "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"[DONE] {task_entry}"
                        else:
                            task_entry = f"[TODO] {task_entry}"
                        task_list.append(task_entry)

                    return f"Here are your {priority} priority tasks ({len(tasks)} total):\n" + "\n".join(task_list)
                except Exception as e:
                    logger.error(f"Error filtering tasks by priority: {str(e)}")
                    return "Sorry, I couldn't filter your tasks by priority. Please try again."

        # NEW: Pattern for "show tasks with [tag] tag" (alternative version) → filter_tasks
        show_tasks_with_tag_alt_match = re.search(r'^show tasks with (.+?) tag$', user_message.strip())
        if show_tasks_with_tag_alt_match:
            tag = show_tasks_with_tag_alt_match.group(1).strip()

            try:
                # Use filter_tasks function with tags
                filter_result = await filter_tasks(
                    user_id=user_id,
                    tags=[tag],
                    db_session=db_session
                )

                tasks = filter_result["tasks"]

                if not tasks:
                    return f"No tasks found with '{tag}' tag."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Here are your tasks with '{tag}' tag ({len(tasks)} total):\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error filtering tasks by tag: {str(e)}")
                return "Sorry, I couldn't filter your tasks by tag. Please try again."

        # Pattern: find tasks tagged (.+) → filter_tasks
        find_tagged_match = re.search(r'^find tasks tagged (.+)$', user_message.strip(), re.IGNORECASE)
        if find_tagged_match:
            tag = find_tagged_match.group(1).strip()

            try:
                # Use filter_tasks function with tags
                filter_result = await filter_tasks(
                    user_id=user_id,
                    tags=[tag],
                    db_session=db_session
                )

                tasks = filter_result["tasks"]

                if not tasks:
                    return f"No tasks found tagged with '{tag}'."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Here are your tasks tagged with '{tag}' ({len(tasks)} total):\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error filtering tasks by tag: {str(e)}")
                return "Sorry, I couldn't filter your tasks by tag. Please try again."

        # Pattern: show tasks with (.+) tag → filter_tasks
        show_tag_match = re.search(r'^show tasks with (.+) tag$', user_message.strip(), re.IGNORECASE)
        if show_tag_match:
            tag = show_tag_match.group(1).strip()

            try:
                # Use filter_tasks function with tags
                filter_result = await filter_tasks(
                    user_id=user_id,
                    tags=[tag],
                    db_session=db_session
                )

                tasks = filter_result["tasks"]

                if not tasks:
                    return f"No tasks found with '{tag}' tag."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Here are your tasks with '{tag}' tag ({len(tasks)} total):\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error filtering tasks by tag: {str(e)}")
                return "Sorry, I couldn't filter your tasks by tag. Please try again."

        # Pattern: tasks with (.+) tag → filter_tasks
        filter_match = re.search(r'^tasks with (.+) tag$', user_message.strip())
        if filter_match:
            tag = filter_match.group(1).strip()

            try:
                # Use filter_tasks function with tags
                filter_result = await filter_tasks(
                    user_id=user_id,
                    tags=[tag],
                    db_session=db_session
                )

                tasks = filter_result["tasks"]

                if not tasks:
                    return f"No tasks found with '{tag}' tag."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Here are your tasks with '{tag}' tag ({len(tasks)} total):\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error filtering tasks by tag: {str(e)}")
                return "Sorry, I couldn't filter your tasks by tag. Please try again."

        # NEW: Pattern for "show me [priority] tasks" → filter_tasks
        priority_filter_match = re.search(r'^show me (.+?) tasks$', user_message.strip())
        if priority_filter_match:
            potential_priority_phrase = priority_filter_match.group(1).strip()

            # Check if it's a priority filter - look for priority in the phrase
            common_priorities = ['high', 'medium', 'low']

            # Extract priority from the phrase (e.g., "high priority", "high", "high priority urgent", etc.)
            found_priority = None
            for priority in common_priorities:
                if priority in potential_priority_phrase.lower():
                    found_priority = priority
                    break

            if found_priority:
                priority = found_priority

                try:
                    # Use filter_tasks function with priority
                    filter_result = await filter_tasks(
                        user_id=user_id,
                        priority=[priority],  # Note: filter_tasks expects a list
                        db_session=db_session
                    )

                    tasks = filter_result["tasks"]

                    if not tasks:
                        return f"No {priority} priority tasks found."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "HIGH "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "MED "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "LOW "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"[DONE] {task_entry}"
                        else:
                            task_entry = f"[TODO] {task_entry}"
                        task_list.append(task_entry)

                    return f"Here are your {priority} priority tasks ({len(tasks)} total):\n" + "\n".join(task_list)
                except Exception as e:
                    logger.error(f"Error filtering tasks by priority: {str(e)}")
                    return "Sorry, I couldn't filter your tasks by priority. Please try again."

        # NEW: Pattern for "filter tasks by [category] category" → filter_tasks
        category_filter_match = re.search(r'^filter tasks by (\w+) category$', user_message.strip(), re.IGNORECASE)
        if category_filter_match:
            category = category_filter_match.group(1).strip()

            try:
                # Use filter_tasks function with category
                filter_result = await filter_tasks(
                    user_id=user_id,
                    category=category,
                    db_session=db_session
                )

                tasks = filter_result["tasks"]

                if not tasks:
                    return f"No tasks found in '{category}' category."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Here are your {category} category tasks ({len(tasks)} total):\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error filtering tasks by category: {str(e)}")
                return "Sorry, I couldn't filter your tasks by category. Please try again."

        # Alternative pattern for "filter tasks by [category]" (more general)
        general_category_filter_match = re.search(r'^filter tasks by (\w+)$', user_message.strip(), re.IGNORECASE)
        if general_category_filter_match:
            category = general_category_filter_match.group(1).strip()

            try:
                # Use filter_tasks function with category
                filter_result = await filter_tasks(
                    user_id=user_id,
                    category=category,
                    db_session=db_session
                )

                tasks = filter_result["tasks"]

                if not tasks:
                    return f"No tasks found in '{category}' category."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Here are your {category} category tasks ({len(tasks)} total):\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error filtering tasks by category: {str(e)}")
                return "Sorry, I couldn't filter your tasks by category. Please try again."

        # NEW: Pattern for "list [category] tasks" → filter_tasks
        list_category_match = re.search(r'^list (\w+) tasks$', user_message.strip())
        if list_category_match:
            category = list_category_match.group(1).strip()

            # Only process if it's a common category to avoid conflicts with other commands
            common_categories = ['work', 'personal', 'shopping', 'urgent', 'home']
            if category in common_categories:
                try:
                    # Use filter_tasks function with category
                    filter_result = await filter_tasks(
                        user_id=user_id,
                        category=category,
                        db_session=db_session
                    )

                    tasks = filter_result["tasks"]

                    if not tasks:
                        return f"No {category} tasks found."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "HIGH "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "MED "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "LOW "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"[DONE] {task_entry}"
                        else:
                            task_entry = f"[TODO] {task_entry}"
                        task_list.append(task_entry)

                    return f"Here are your {category} tasks ({len(tasks)} total):\n" + "\n".join(task_list)
                except Exception as e:
                    logger.error(f"Error filtering tasks by category: {str(e)}")
                    return "Sorry, I couldn't filter your tasks by category. Please try again."

        # NEW: Pattern for "show [category] tasks" → filter_tasks
        show_category_match = re.search(r'^show (\w+) tasks$', user_message.strip())
        if show_category_match:
            category = show_category_match.group(1).strip()

            # Only process if it's a common category to avoid conflicts with other commands
            common_categories = ['work', 'personal', 'shopping', 'urgent', 'home']
            if category in common_categories:
                try:
                    # Use filter_tasks function with category
                    filter_result = await filter_tasks(
                        user_id=user_id,
                        category=category,
                        db_session=db_session
                    )

                    tasks = filter_result["tasks"]

                    if not tasks:
                        return f"No {category} tasks found."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "HIGH "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "MED "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "LOW "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"[DONE] {task_entry}"
                        else:
                            task_entry = f"[TODO] {task_entry}"
                        task_list.append(task_entry)

                    return f"Here are your {category} tasks ({len(tasks)} total):\n" + "\n".join(task_list)
                except Exception as e:
                    logger.error(f"Error filtering tasks by category: {str(e)}")
                    return "Sorry, I couldn't filter your tasks by category. Please try again."

        # NEW: Pattern for "filter by [tag] tag" → filter_tasks
        filter_by_tag_match = re.search(r'^filter by (.+) tag$', user_message.strip())
        if filter_by_tag_match:
            tag = filter_by_tag_match.group(1).strip()

            try:
                # Use filter_tasks function with tags
                filter_result = await filter_tasks(
                    user_id=user_id,
                    tags=[tag],
                    db_session=db_session
                )

                tasks = filter_result["tasks"]

                if not tasks:
                    return f"No tasks found with '{tag}' tag."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Here are your tasks with '{tag}' tag ({len(tasks)} total):\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error filtering tasks by tag: {str(e)}")
                return "Sorry, I couldn't filter your tasks by tag. Please try again."

        # Pattern: what('s| is) my completion rate → get_task_stats
        stats_match = re.search(r"what(\'s| is) my completion rate", user_message.strip())
        if stats_match:
            try:
                stats_result = await get_task_stats(user_id=user_id, timeframe=None, db_session=db_session)

                stats = stats_result["stats"]
                total = stats["total_tasks"]
                completed = stats["completed_tasks"]
                pending = stats["pending_tasks"]
                completion_pct = stats["completion_percentage"]

                response = f"Here are your task statistics:\n"
                response += f"• Total tasks: {total}\n"
                response += f"• Completed: {completed}\n"
                response += f"• Pending: {pending}\n"
                response += f"• Completion rate: {completion_pct}%\n"

                return response
            except Exception as e:
                logger.error(f"Error getting task stats: {str(e)}")
                return "Sorry, I couldn't retrieve your task statistics. Please try again."

        # Pattern: complete all the tasks (generic - all tasks) → bulk_operations
        complete_all_generic_match = re.search(r'^complete all (?:the )?tasks$', user_message.strip())
        if complete_all_generic_match:
            try:
                # Get all pending tasks and complete them
                all_tasks_result = await list_tasks(user_id=user_id, completed=False, db_session=db_session)
                all_tasks = all_tasks_result["tasks"]

                completed_count = 0
                for task in all_tasks:
                    if not task.get("completed"):  # Only complete if not already completed
                        await complete_task(
                            user_id=user_id,
                            task_id=task["task_id"],
                            db_session=db_session
                        )
                        completed_count += 1

                return f"I've completed {completed_count} tasks for you."
            except Exception as e:
                logger.error(f"Error performing bulk operation: {str(e)}")
                return f"Sorry, I couldn't complete all tasks. Error: {str(e)}"

        # Pattern: complete all X tasks (specific category) → bulk_operations
        complete_all_category_match = re.search(r'^complete all (?:the )?(.+?) tasks$', user_message.strip())
        if complete_all_category_match:
            category = complete_all_category_match.group(1).strip()

            # Only process if the category is not a generic word that would match the previous pattern
            if category.lower() not in ['the', 'all', '']:  # Only process specific categories
                try:
                    # Use filter criteria to find tasks by tag/category
                    bulk_result = await bulk_operations(
                        user_id=user_id,
                        operation="complete",
                        filter_criteria={"tags": [category]},
                        db_session=db_session
                    )

                    affected_count = bulk_result.get("affected_task_count", 0)
                    return f"I've completed {affected_count} {category} tasks for you."
                except Exception as e:
                    logger.error(f"Error performing bulk operation: {str(e)}")
                    return f"Sorry, I couldn't complete all {category} tasks. Error: {str(e)}"

        # Pattern: create (.+) priority (.+) task: (.+) → add_task_with_details
        create_task_match = re.search(r'^create (.+) priority (.+) task: (.+)$', user_message.strip())
        if create_task_match:
            priority = create_task_match.group(1).strip()
            title = create_task_match.group(2).strip()
            description = create_task_match.group(3).strip()

            try:
                # Create task with details
                result = await add_task_with_details(
                    user_id=user_id,
                    title=title,
                    priority=priority,
                    description=description,
                    db_session=db_session
                )

                return f"I've added '{title}' as a {priority} priority task: {description}."
            except Exception as e:
                logger.error(f"Error adding task with details: {str(e)}")
                return f"Sorry, I couldn't add the task. Error: {str(e)}"

        # NEW: Pattern for "add [priority] [category] task: [title]" → add_task_with_details
        detailed_add_match = re.search(r'^add\s+(.+?)\s+(.+?)\s+task:\s+(.+)$', user_message.strip())
        if detailed_add_match:
            priority_or_category = detailed_add_match.group(1).strip()
            category_or_title = detailed_add_match.group(2).strip()
            title_or_rest = detailed_add_match.group(3).strip()

            # Determine which is priority and which is category based on common values
            common_priorities = ['high', 'medium', 'low']
            common_categories = ['work', 'personal', 'shopping', 'urgent', 'home']

            priority = None
            category = None
            title = title_or_rest
            tags = []

            # Check if first part is a priority or category
            if priority_or_category in common_priorities:
                priority = priority_or_category
                if category_or_title in common_categories:
                    category = category_or_title
                else:
                    # Assume second part is the title if it's not a known category
                    title = f"{category_or_title} {title_or_rest}".strip()
            elif priority_or_category in common_categories:
                category = priority_or_category
                if category_or_title in common_priorities:
                    priority = category_or_title
                else:
                    # Assume second part is the title if it's not a known priority
                    title = f"{category_or_title} {title_or_rest}".strip()
            else:
                # Neither is a known priority or category, assume first is category
                category = priority_or_category
                title = f"{category_or_title} {title_or_rest}".strip()

            # Extract tags from the title/description part
            # Look for patterns like "with urgent tag" or "with work and personal tags"
            tag_pattern = r'with\s+(.+?)\s+tag(?:s?)'
            tag_match = re.search(tag_pattern, title.lower())
            if tag_match:
                tag_part = tag_match.group(1).strip()
                # Split tags by 'and' or commas
                raw_tags = re.split(r'\s+and\s+|\s*,\s*', tag_part)
                for raw_tag in raw_tags:
                    clean_tag = raw_tag.strip()
                    if clean_tag and clean_tag not in tags:
                        tags.append(clean_tag)

                # Remove the tag part from the title
                title = re.sub(tag_pattern, '', title, flags=re.IGNORECASE).strip()
                title = re.sub(r'\s+', ' ', title).strip()  # Clean up extra spaces

            try:
                # Create task with details
                result = await add_task_with_details(
                    user_id=user_id,
                    title=title,
                    priority=priority,
                    category=category,
                    tags=tags if tags else None,
                    db_session=db_session
                )

                priority_str = f"{priority} priority " if priority else ""
                category_str = f"for {category} " if category else ""
                tags_str = f" with tags: {', '.join(tags)}" if tags else ""
                return f"I've added '{title}' as a {priority_str}{category_str}task.{tags_str}"
            except Exception as e:
                logger.error(f"Error adding task with details: {str(e)}")
                return f"Sorry, I couldn't add the task. Error: {str(e)}"

        # NEW: Pattern for "add [category] task: [title] with [tag] tag" → add_task_with_details
        detailed_add_match_colon = re.search(r'^add\s+(\w+)\s+task:\s+(.+)$', user_message.strip())
        if detailed_add_match_colon:
            category = detailed_add_match_colon.group(1).strip()
            title_with_possible_tags = detailed_add_match_colon.group(2).strip()

            title = title_with_possible_tags
            tags = []

            # Extract tags from the title part
            # Look for patterns like "with urgent tag" or "with work and personal tags"
            tag_pattern = r'with\s+(.+?)\s+tag(?:s?)'
            tag_match = re.search(tag_pattern, title.lower())
            if tag_match:
                tag_part = tag_match.group(1).strip()
                # Split tags by 'and' or commas
                raw_tags = re.split(r'\s+and\s+|\s*,\s*', tag_part)
                for raw_tag in raw_tags:
                    clean_tag = raw_tag.strip()
                    if clean_tag and clean_tag not in tags:
                        tags.append(clean_tag)

                # Remove the tag part from the title
                title = re.sub(tag_pattern, '', title, flags=re.IGNORECASE).strip()
                title = re.sub(r'\s+', ' ', title).strip()  # Clean up extra spaces

            # Validate that the category is a common category
            common_categories = ['work', 'personal', 'shopping', 'urgent', 'home', 'family']
            if category not in common_categories:
                # If it's not a common category, treat it as a regular add task
                pass
            else:
                try:
                    # Create task with details
                    result = await add_task_with_details(
                        user_id=user_id,
                        title=title,
                        category=category,
                        tags=tags if tags else None,
                        db_session=db_session
                    )

                    category_str = f"for {category} " if category else ""
                    tags_str = f" with tags: {', '.join(tags)}" if tags else ""
                    return f"I've added '{title}' as a {category_str}task.{tags_str}"
                except Exception as e:
                    logger.error(f"Error adding task with details: {str(e)}")
                    return f"Sorry, I couldn't add the task. Error: {str(e)}"

        # NEW: Pattern for "add [priority] [category] task [title]" (without colon) → add_task_with_details
        detailed_add_match2 = re.search(r'^add\s+(.+?)\s+(.+?)\s+task\s+(.+)$', user_message.strip())
        if detailed_add_match2:
            priority_or_category = detailed_add_match2.group(1).strip()
            category_or_title = detailed_add_match2.group(2).strip()
            title_or_rest = detailed_add_match2.group(3).strip()

            # Determine which is priority and which is category based on common values
            common_priorities = ['high', 'medium', 'low']
            common_categories = ['work', 'personal', 'shopping', 'urgent', 'home']

            priority = None
            category = None
            title = title_or_rest
            tags = []

            # Check if first part is a priority or category
            if priority_or_category in common_priorities:
                priority = priority_or_category
                if category_or_title in common_categories:
                    category = category_or_title
                else:
                    # Assume second part is the title if it's not a known category
                    title = f"{category_or_title} {title_or_rest}".strip()
            elif priority_or_category in common_categories:
                category = priority_or_category
                if category_or_title in common_priorities:
                    priority = category_or_title
                else:
                    # Assume second part is the title if it's not a known priority
                    title = f"{category_or_title} {title_or_rest}".strip()
            else:
                # Neither is a known priority or category, assume first is category
                category = priority_or_category
                title = f"{category_or_title} {title_or_rest}".strip()

            # Extract tags from the title/description part
            # Look for patterns like "with urgent tag" or "with work and personal tags"
            tag_pattern = r'with\s+(.+?)\s+tag(?:s?)'
            tag_match = re.search(tag_pattern, title.lower())
            if tag_match:
                tag_part = tag_match.group(1).strip()
                # Split tags by 'and' or commas
                raw_tags = re.split(r'\s+and\s+|\s*,\s*', tag_part)
                for raw_tag in raw_tags:
                    clean_tag = raw_tag.strip()
                    if clean_tag and clean_tag not in tags:
                        tags.append(clean_tag)

                # Remove the tag part from the title
                title = re.sub(tag_pattern, '', title, flags=re.IGNORECASE).strip()
                title = re.sub(r'\s+', ' ', title).strip()  # Clean up extra spaces

            try:
                # Create task with details
                result = await add_task_with_details(
                    user_id=user_id,
                    title=title,
                    priority=priority,
                    category=category,
                    tags=tags if tags else None,
                    db_session=db_session
                )

                priority_str = f"{priority} priority " if priority else ""
                category_str = f"for {category} " if category else ""
                tags_str = f" with tags: {', '.join(tags)}" if tags else ""
                return f"I've added '{title}' as a {priority_str}{category_str}task.{tags_str}"
            except Exception as e:
                logger.error(f"Error adding task with details: {str(e)}")
                return f"Sorry, I couldn't add the task. Error: {str(e)}"

        # Pattern: find tasks containing (.+) → search_tasks
        find_containing_match = re.search(r'^find tasks containing (.+)$', user_message.strip(), re.IGNORECASE)
        if find_containing_match:
            query = find_containing_match.group(1).strip()

            try:
                search_result = await search_tasks(
                    user_id=user_id,
                    query=query,
                    search_in=['title', 'description', 'tags'],
                    db_session=db_session
                )

                tasks = search_result["tasks"]

                if not tasks:
                    return f"No tasks found containing '{query}'."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Found {len(tasks)} tasks containing '{query}':\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error searching tasks: {str(e)}")
                return "Sorry, I couldn't search your tasks. Please try again."

        # Pattern: search tasks for (.+) → search_tasks
        search_tasks_match = re.search(r'^search tasks for (.+)$', user_message.strip(), re.IGNORECASE)
        if search_tasks_match:
            query = search_tasks_match.group(1).strip()

            try:
                search_result = await search_tasks(
                    user_id=user_id,
                    query=query,
                    search_in=['title', 'description', 'tags'],
                    db_session=db_session
                )

                tasks = search_result["tasks"]

                if not tasks:
                    return f"No tasks found matching '{query}'."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Found {len(tasks)} tasks matching '{query}':\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error searching tasks: {str(e)}")
                return "Sorry, I couldn't search your tasks. Please try again."

        # Pattern: search for (.+) → search_tasks
        search_match = re.search(r'^search for (.+)$', user_message.strip())
        if search_match:
            query = search_match.group(1).strip()

            try:
                search_result = await search_tasks(
                    user_id=user_id,
                    query=query,
                    search_in=['title', 'description', 'tags'],
                    db_session=db_session
                )

                tasks = search_result["tasks"]

                if not tasks:
                    return f"No tasks found matching '{query}'."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Found {len(tasks)} tasks matching '{query}':\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error searching tasks: {str(e)}")
                return "Sorry, I couldn't search your tasks. Please try again."

        # NEW: Pattern for "find tasks containing [query]" (alternative to "find tasks with [query]") → search_tasks
        find_tasks_containing_match = re.search(r'^find tasks containing (.+)$', user_message.strip(), re.IGNORECASE)
        if find_tasks_containing_match:
            query = find_tasks_containing_match.group(1).strip()

            try:
                search_result = await search_tasks(
                    user_id=user_id,
                    query=query,
                    search_in=['title', 'description', 'tags'],
                    db_session=db_session
                )

                tasks = search_result["tasks"]

                if not tasks:
                    return f"No tasks found containing '{query}'."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Found {len(tasks)} tasks containing '{query}':\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error searching tasks: {str(e)}")
                return "Sorry, I couldn't search your tasks. Please try again."

        # NEW: Pattern for "find tasks with [query]" (different from "find tasks tagged") → search_tasks
        find_tasks_with_query_match = re.search(r'^find tasks with (.+)$', user_message.strip(), re.IGNORECASE)
        if find_tasks_with_query_match:
            query = find_tasks_with_query_match.group(1).strip()

            # Avoid conflict with tag-based patterns
            common_tags = ['work', 'personal', 'shopping', 'urgent', 'home', 'high', 'medium', 'low']
            if query.lower() in common_tags:
                pass  # Let other handlers manage these
            else:
                try:
                    search_result = await search_tasks(
                        user_id=user_id,
                        query=query,
                        search_in=['title', 'description', 'tags'],
                        db_session=db_session
                    )

                    tasks = search_result["tasks"]

                    if not tasks:
                        return f"No tasks found with '{query}'."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "HIGH "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "MED "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "LOW "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"[DONE] {task_entry}"
                        else:
                            task_entry = f"[TODO] {task_entry}"
                        task_list.append(task_entry)

                    return f"Found {len(tasks)} tasks with '{query}':\n" + "\n".join(task_list)
                except Exception as e:
                    logger.error(f"Error searching tasks: {str(e)}")
                    return "Sorry, I couldn't search your tasks. Please try again."

        # NEW: Pattern for "search for [query] tasks" (reversed order) → search_tasks
        search_for_tasks_match = re.search(r'^search for (.+) tasks$', user_message.strip(), re.IGNORECASE)
        if search_for_tasks_match:
            query = search_for_tasks_match.group(1).strip()

            # Avoid conflict with tag/priority patterns
            common_categories = ['work', 'personal', 'shopping', 'urgent', 'home', 'high', 'medium', 'low']
            if query.lower() in common_categories:
                pass  # Let other handlers manage these
            else:
                try:
                    search_result = await search_tasks(
                        user_id=user_id,
                        query=query,
                        search_in=['title', 'description', 'tags'],
                        db_session=db_session
                    )

                    tasks = search_result["tasks"]

                    if not tasks:
                        return f"No tasks found matching '{query}'."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "HIGH "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "MED "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "LOW "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"[DONE] {task_entry}"
                        else:
                            task_entry = f"[TODO] {task_entry}"
                        task_list.append(task_entry)

                    return f"Found {len(tasks)} tasks matching '{query}':\n" + "\n".join(task_list)
                except Exception as e:
                    logger.error(f"Error searching tasks: {str(e)}")
                    return "Sorry, I couldn't search your tasks. Please try again."

        # Pattern: what tasks are due (.+) → filter_tasks with date filter
        due_tasks_match = re.search(r'what tasks are due (.+)|tasks due (.+)', user_message.strip(), re.IGNORECASE)
        if due_tasks_match:
            date_desc = due_tasks_match.group(1) or due_tasks_match.group(2)

            # Extract the specific date from the message
            due_date = extract_due_date(user_message.lower())

            if due_date:
                try:
                    # Use filter_tasks function with date filter
                    filter_result = await filter_tasks(
                        user_id=user_id,
                        date_to=due_date,
                        date_from=due_date,  # Same date for exact match
                        db_session=db_session
                    )

                    tasks = filter_result["tasks"]

                    if not tasks:
                        return f"No tasks are due on {due_date}."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "HIGH "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "MED "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "LOW "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"[DONE] {task_entry}"
                        else:
                            task_entry = f"[TODO] {task_entry}"
                        task_list.append(task_entry)

                    return f"Here are your tasks due on {due_date} ({len(tasks)} total):\n" + "\n".join(task_list)
                except Exception as e:
                    logger.error(f"Error filtering tasks by due date: {str(e)}")
                    return "Sorry, I couldn't filter your tasks by due date. Please try again."

        # NEW: Pattern for "what's due [timeframe]" (contraction support) → filter_tasks with date filter
        due_tasks_contractions_match = re.search(r"(what's|whats|what is) due (.+)", user_message.strip(), re.IGNORECASE)
        if due_tasks_contractions_match:
            date_desc = due_tasks_contractions_match.group(2)

            # Extract the specific date from the message
            due_date = extract_due_date(user_message.lower())

            if due_date:
                try:
                    # Use filter_tasks function with date filter
                    filter_result = await filter_tasks(
                        user_id=user_id,
                        date_to=due_date,
                        date_from=due_date,  # Same date for exact match
                        db_session=db_session
                    )

                    tasks = filter_result["tasks"]

                    if not tasks:
                        return f"No tasks are due on {due_date}."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "HIGH "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "MED "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "LOW "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"[DONE] {task_entry}"
                        else:
                            task_entry = f"[TODO] {task_entry}"
                        task_list.append(task_entry)

                    return f"Here are your tasks due on {due_date} ({len(tasks)} total):\n" + "\n".join(task_list)
                except Exception as e:
                    logger.error(f"Error filtering tasks by due date: {str(e)}")
                    return "Sorry, I couldn't filter your tasks by due date. Please try again."

        # Pattern: arrange tasks by (.+) or sort tasks by (.+) or order tasks by (.+) → list_tasks with sort parameters
        sort_tasks_match = re.search(r'arrange tasks by (.+)|sort tasks by (.+)|order tasks by (.+)', user_message.strip(), re.IGNORECASE)
        if sort_tasks_match:
            sort_field = sort_tasks_match.group(1) or sort_tasks_match.group(2) or sort_tasks_match.group(3)

            # Determine sort parameters based on the field specified
            sort_by = None
            sort_order = 'asc'

            sort_field_lower = sort_field.lower().strip()
            if 'title' in sort_field_lower or 'name' in sort_field_lower:
                sort_by = 'title'
            elif 'due date' in sort_field_lower or 'due' in sort_field_lower or 'date' in sort_field_lower:
                sort_by = 'due_date'
            elif 'priority' in sort_field_lower:
                sort_by = 'priority'
            elif 'created' in sort_field_lower:
                sort_by = 'created_at'
            elif 'updated' in sort_field_lower:
                sort_by = 'updated_at'

            if sort_by:
                try:
                    # Use list_tasks function with sort parameters
                    sort_result = await list_tasks(
                        user_id=user_id,
                        completed=None,
                        sort_by=sort_by,
                        sort_order=sort_order,
                        db_session=db_session
                    )

                    tasks = sort_result["tasks"]

                    if not tasks:
                        return "You have no tasks."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "HIGH "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "MED "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "LOW "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"[DONE] {task_entry}"
                        else:
                            task_entry = f"[TODO] {task_entry}"
                        task_list.append(task_entry)

                    sort_description = sort_by.replace('_', ' ')
                    return f"Here are your tasks ordered by {sort_description} ({len(tasks)} total):\n" + "\n".join(task_list)
                except Exception as e:
                    logger.error(f"Error sorting tasks: {str(e)}")
                    return "Sorry, I couldn't sort your tasks. Please try again."
            else:
                # If we couldn't determine a sort field, fall back to the default behavior
                pass

        # NEW: Pattern for "create [category] task: [title]" → add_task_with_details
        create_category_task_match = re.search(r'^create (\w+) task: (.+)$', user_message.strip())
        if create_category_task_match:
            category = create_category_task_match.group(1).strip()
            title = create_category_task_match.group(2).strip()

            try:
                # Create task with category
                result = await add_task_with_details(
                    user_id=user_id,
                    title=title,
                    category=category,
                    db_session=db_session
                )

                return f"I've added '{title}' as a {category} task."
            except Exception as e:
                logger.error(f"Error adding category task: {str(e)}")
                return f"Sorry, I couldn't add the task. Error: {str(e)}"

        # NEW: Pattern for "list tasks having [tag] tag" → filter_tasks
        list_having_tag_match = re.search(r'^list tasks having (.+) tag$', user_message.strip())
        if list_having_tag_match:
            tag = list_having_tag_match.group(1).strip()

            try:
                # Use filter_tasks function with tags
                filter_result = await filter_tasks(
                    user_id=user_id,
                    tags=[tag],
                    db_session=db_session
                )

                tasks = filter_result["tasks"]

                if not tasks:
                    return f"No tasks found having '{tag}' tag."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Here are your tasks having '{tag}' tag ({len(tasks)} total):\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error filtering tasks by tag: {str(e)}")
                return "Sorry, I couldn't filter your tasks by tag. Please try again."

        # NEW: Pattern for "look for [query] in tasks" → search_tasks
        look_for_match = re.search(r'^look for (.+) in tasks$', user_message.strip())
        if look_for_match:
            query = look_for_match.group(1).strip()

            try:
                search_result = await search_tasks(
                    user_id=user_id,
                    query=query,
                    search_in=['title', 'description', 'tags'],
                    db_session=db_session
                )

                tasks = search_result["tasks"]

                if not tasks:
                    return f"No tasks found containing '{query}'."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Found {len(tasks)} tasks containing '{query}':\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error searching tasks: {str(e)}")
                return "Sorry, I couldn't search your tasks. Please try again."

        # NEW: Pattern for "list [priority] priority tasks" → filter_tasks
        list_priority_tasks_match = re.search(r'^list (.+) priority tasks$', user_message.strip())
        if list_priority_tasks_match:
            priority = list_priority_tasks_match.group(1).strip()

            # Only process if it's a valid priority
            valid_priorities = ['high', 'medium', 'low']
            if priority.lower() in valid_priorities:
                try:
                    # Use filter_tasks function with priority
                    filter_result = await filter_tasks(
                        user_id=user_id,
                        priority=[priority.lower()],  # Note: filter_tasks expects a list
                        db_session=db_session
                    )

                    tasks = filter_result["tasks"]

                    if not tasks:
                        return f"No {priority} priority tasks found."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "HIGH "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "MED "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "LOW "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"[DONE] {task_entry}"
                        else:
                            task_entry = f"[TODO] {task_entry}"
                        task_list.append(task_entry)

                    return f"Here are your {priority} priority tasks ({len(tasks)} total):\n" + "\n".join(task_list)
                except Exception as e:
                    logger.error(f"Error filtering tasks by priority: {str(e)}")
                    return "Sorry, I couldn't filter your tasks by priority. Please try again."

        # NEW: Pattern for "display [priority] priority tasks" → filter_tasks
        display_priority_tasks_match = re.search(r'^display (.+) priority tasks$', user_message.strip())
        if display_priority_tasks_match:
            priority = display_priority_tasks_match.group(1).strip()

            # Only process if it's a valid priority
            valid_priorities = ['high', 'medium', 'low']
            if priority.lower() in valid_priorities:
                try:
                    # Use filter_tasks function with priority
                    filter_result = await filter_tasks(
                        user_id=user_id,
                        priority=[priority.lower()],  # Note: filter_tasks expects a list
                        db_session=db_session
                    )

                    tasks = filter_result["tasks"]

                    if not tasks:
                        return f"No {priority} priority tasks found."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "HIGH "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "MED "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "LOW "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"[DONE] {task_entry}"
                        else:
                            task_entry = f"[TODO] {task_entry}"
                        task_list.append(task_entry)

                    return f"Here are your {priority} priority tasks ({len(tasks)} total):\n" + "\n".join(task_list)
                except Exception as e:
                    logger.error(f"Error filtering tasks by priority: {str(e)}")
                    return "Sorry, I couldn't filter your tasks by priority. Please try again."

        # NEW: Pattern for "list overdue tasks" → filter_tasks
        list_overdue_match = re.search(r'^list overdue tasks$', user_message.strip())
        if list_overdue_match:
            try:
                # Use filter_tasks function with date filter for overdue tasks
                from datetime import datetime
                current_date = datetime.now().strftime('%Y-%m-%d')

                filter_result = await filter_tasks(
                    user_id=user_id,
                    date_to=current_date,  # Tasks due on or before today
                    completed=False,  # Only incomplete tasks
                    db_session=db_session
                )

                tasks = filter_result["tasks"]

                if not tasks:
                    return "No overdue tasks found."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Here are your overdue tasks ({len(tasks)} total):\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error filtering overdue tasks: {str(e)}")
                return "Sorry, I couldn't filter your overdue tasks. Please try again."

        # NEW: Pattern for "arrange tasks by due date" → list_tasks with sort parameters
        arrange_by_due_date_match = re.search(r'^arrange tasks by due date$', user_message.strip())
        if arrange_by_due_date_match:
            try:
                # Use list_tasks function with sort parameters for due date
                sort_result = await list_tasks(
                    user_id=user_id,
                    completed=None,
                    sort_by='due_date',
                    sort_order='asc',  # Ascending order (soonest due first)
                    db_session=db_session
                )

                tasks = sort_result["tasks"]

                if not tasks:
                    return "You have no tasks."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Here are your tasks arranged by due date ({len(tasks)} total):\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error sorting tasks by due date: {str(e)}")
                return "Sorry, I couldn't sort your tasks by due date. Please try again."

        # Pattern: Show high priority work tasks due this week → filter_tasks with multiple filters
        combined_query_match = re.search(r'show (.*) tasks? due (.*)|tasks? (.*) due (.*)', user_message.strip(), re.IGNORECASE)
        if combined_query_match:
            # Check if this is a combined query with priority and category like "high priority work tasks"
            text_parts = user_message.lower().split()

            # Extract priority
            priority = None
            if 'high' in text_parts and ('priority' in text_parts or 'priorities' in text_parts):
                priority = 'high'
            elif 'medium' in text_parts and ('priority' in text_parts or 'priorities' in text_parts):
                priority = 'medium'
            elif 'low' in text_parts and ('priority' in text_parts or 'priorities' in text_parts):
                priority = 'low'

            # Extract category (common ones)
            category = None
            common_categories = ['work', 'personal', 'shopping', 'urgent', 'home', 'family']
            for cat in common_categories:
                if cat in text_parts:
                    category = cat
                    break

            # Extract due date range
            due_date_info = extract_due_date(user_message.lower())
            date_from = None
            date_to = None

            if due_date_info and 'week' in user_message.lower():
                # If it's "this week", set the full week range
                from datetime import datetime, timedelta
                start_of_week = datetime.fromisoformat(due_date_info)
                end_of_week = start_of_week + timedelta(days=6)  # End of the week (Sunday)
                date_from = start_of_week.strftime('%Y-%m-%d')
                date_to = end_of_week.strftime('%Y-%m-%d')
            elif due_date_info:
                # For other dates, set same date range
                date_from = date_to = due_date_info

            # Only process if we have at least one filter criterion
            if priority or category or date_from or date_to:
                try:
                    # Use filter_tasks function with multiple filters
                    filter_params = {
                        'user_id': user_id,
                        'db_session': db_session
                    }

                    if priority:
                        filter_params['priority'] = [priority]
                    if category:
                        filter_params['category'] = category
                    if date_from:
                        filter_params['date_from'] = date_from
                    if date_to:
                        filter_params['date_to'] = date_to

                    filter_result = await filter_tasks(**filter_params)
                    tasks = filter_result["tasks"]

                    if not tasks:
                        response_parts = ["No tasks found"]
                        if priority:
                            response_parts.append(f"with {priority} priority")
                        if category:
                            response_parts.append(f"in {category} category")
                        if date_from and date_to:
                            response_parts.append(f"due between {date_from} and {date_to}")
                        elif date_from:
                            response_parts.append(f"due on {date_from}")
                        return " ".join(response_parts) + "."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "HIGH "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "MED "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "LOW "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"[DONE] {task_entry}"
                        else:
                            task_entry = f"[TODO] {task_entry}"
                        task_list.append(task_entry)

                    # Build a descriptive response based on filters applied
                    desc_parts = []
                    if priority:
                        desc_parts.append(f"{priority} priority")
                    if category:
                        desc_parts.append(f"{category}")
                    if date_from and date_to and 'week' in user_message.lower():
                        desc_parts.append("this week")
                    elif date_from:
                        desc_parts.append(f"due on {date_from}")

                    filters_desc = " ".join(desc_parts) if desc_parts else "matching criteria"

                    return f"Here are your {filters_desc} tasks ({len(tasks)} total):\n" + "\n".join(task_list)
                except Exception as e:
                    logger.error(f"Error filtering tasks with combined criteria: {str(e)}")
                    return "Sorry, I couldn't filter your tasks with the specified criteria. Please try again."

        # NEW: Pattern for "finish task [num]" (alternative to "complete task") → complete_task
        finish_task_num_match = re.search(r'^finish task (\d+)$', user_message.strip())
        if finish_task_num_match:
            task_num = int(finish_task_num_match.group(1))
            print(f"[DEBUG] Calling complete_task for task {task_num}")

            # Get all tasks to map by position
            all_tasks_result = await list_tasks(user_id=user_id, completed=None, db_session=db_session)
            all_tasks = all_tasks_result["tasks"]

            # Convert the number to an index (1-based to 0-based)
            task_idx = task_num - 1

            if 0 <= task_idx < len(all_tasks):
                task_to_update_obj = all_tasks[task_idx]
                task_id = task_to_update_obj["task_id"]

                # Call the complete_task function directly
                result = await complete_task(
                    user_id=user_id,
                    task_id=task_id,
                    db_session=db_session
                )
                return f"I've marked task '{task_to_update_obj['title']}' as completed."
            else:
                return f"Could not find task number {task_num}. Please specify a number between 1 and {len(all_tasks)}."

        # NEW: Pattern for "remove task [num]" (alternative to "delete task") → delete_task
        remove_task_num_match = re.search(r'^remove task (\d+)$', user_message.strip())
        if remove_task_num_match:
            task_num = int(remove_task_num_match.group(1))
            print(f"[DEBUG] Calling delete_task for task {task_num}")

            # Get all tasks to map by position
            all_tasks_result = await list_tasks(user_id=user_id, completed=None, db_session=db_session)
            all_tasks = all_tasks_result["tasks"]

            # Convert the number to an index (1-based to 0-based)
            task_idx = task_num - 1

            # Add additional safety check to ensure we're not dealing with negative indices
            if task_num <= 0:
                return f"Invalid task number {task_num}. Task numbers must be positive integers."

            if 0 <= task_idx < len(all_tasks):
                task_to_delete_obj = all_tasks[task_idx]
                task_id = task_to_delete_obj["task_id"]

                # Call the delete_task function directly
                result = await delete_task(
                    user_id=user_id,
                    task_id=task_id,
                    db_session=db_session
                )
                return f"I've removed task '{task_to_delete_obj['title']}'."
            else:
                return f"Could not find task number {task_num}. Please specify a number between 1 and {len(all_tasks)}."

        # NEW: Pattern for "mark task [num] as done" → complete_task
        mark_task_done_match = re.search(r'^(?:mark|set|complete) task (\d+) (?:as )?done$', user_message.strip())
        if mark_task_done_match:
            task_num = int(mark_task_done_match.group(1))
            print(f"[DEBUG] Calling complete_task for task {task_num}")

            # Get all tasks to map by position
            all_tasks_result = await list_tasks(user_id=user_id, completed=None, db_session=db_session)
            all_tasks = all_tasks_result["tasks"]

            # Convert the number to an index (1-based to 0-based)
            task_idx = task_num - 1

            if 0 <= task_idx < len(all_tasks):
                task_to_update_obj = all_tasks[task_idx]
                task_id = task_to_update_obj["task_id"]

                # Call the complete_task function directly
                result = await complete_task(
                    user_id=user_id,
                    task_id=task_id,
                    db_session=db_session
                )
                return f"I've marked task '{task_to_update_obj['title']}' as completed."
            else:
                return f"Could not find task number {task_num}. Please specify a number between 1 and {len(all_tasks)}."

        # NEW: Pattern for "find [query] tasks" → search_tasks
        find_tasks_match = re.search(r'^(?:find|search|look for|show me) (.+) tasks$', user_message.strip(), re.IGNORECASE)
        if find_tasks_match:
            query = find_tasks_match.group(1).strip()

            # Avoid triggering on common categories that should be handled differently
            common_categories = ['work', 'personal', 'shopping', 'urgent', 'home', 'high', 'medium', 'low']
            if query.lower() in common_categories:
                pass  # Let other handlers manage these
            else:
                try:
                    search_result = await search_tasks(
                        user_id=user_id,
                        query=query,
                        search_in=['title', 'description', 'tags'],
                        db_session=db_session
                    )

                    tasks = search_result["tasks"]

                    if not tasks:
                        return f"No tasks found matching '{query}'."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "HIGH "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "MED "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "LOW "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"[DONE] {task_entry}"
                        else:
                            task_entry = f"[TODO] {task_entry}"
                        task_list.append(task_entry)

                    return f"Found {len(tasks)} tasks matching '{query}':\n" + "\n".join(task_list)
                except Exception as e:
                    logger.error(f"Error searching tasks: {str(e)}")
                    return "Sorry, I couldn't search your tasks. Please try again."

        # NEW: Pattern for "list all [category] category tasks" → filter_tasks
        list_category_tasks_match = re.search(r'^(?:list|show|display)\s+(?:all\s+)?(\w+)\s+category\s+tasks$', user_message.strip(), re.IGNORECASE)
        if list_category_tasks_match:
            category = list_category_tasks_match.group(1).strip()

            try:
                # Use filter_tasks function with category
                filter_result = await filter_tasks(
                    user_id=user_id,
                    category=category,
                    db_session=db_session
                )

                tasks = filter_result["tasks"]

                if not tasks:
                    return f"No {category} category tasks found."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Here are your {category} category tasks ({len(tasks)} total):\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error filtering tasks by category: {str(e)}")
                return "Sorry, I couldn't filter your tasks by category. Please try again."

        # NEW: Pattern for "filter by [tag] tag" → filter_tasks
        filter_by_tag_match = re.search(r'^(?:filter|show)\s+(?:by|with|having)\s+(\w+)\s+tag$', user_message.strip(), re.IGNORECASE)
        if filter_by_tag_match:
            tag = filter_by_tag_match.group(1).strip()

            try:
                # Use filter_tasks function with tags
                filter_result = await filter_tasks(
                    user_id=user_id,
                    tags=[tag],
                    db_session=db_session
                )

                tasks = filter_result["tasks"]

                if not tasks:
                    return f"No tasks found with '{tag}' tag."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Here are your tasks with '{tag}' tag ({len(tasks)} total):\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error filtering tasks by tag: {str(e)}")
                return "Sorry, I couldn't filter your tasks by tag. Please try again."

        # NEW: Pattern for "order tasks by [field]" → list_tasks with sort parameters
        order_tasks_match = re.search(r'^(?:order|sort|arrange)\s+tasks\s+by\s+(.+)$', user_message.strip(), re.IGNORECASE)
        if order_tasks_match:
            sort_field = order_tasks_match.group(1).strip()

            try:
                # Use list_tasks function with sort parameters
                sort_params = {'sort_by': sort_field, 'sort_order': 'asc'}

                # Adjust sort order based on common expectations
                if sort_field.lower() in ['priority', 'title', 'created_at', 'updated_at']:
                    if sort_field.lower() == 'priority':
                        sort_params['sort_order'] = 'desc'  # High priority first
                    elif sort_field.lower() in ['title']:
                        sort_params['sort_order'] = 'asc'   # Alphabetical
                    elif sort_field.lower() in ['created_at', 'updated_at']:
                        sort_params['sort_order'] = 'desc'  # Newest first
                else:
                    sort_params['sort_by'] = 'created_at'  # Default to creation date

                sort_result = await list_tasks(
                    user_id=user_id,
                    completed=None,
                    sort_by=sort_params.get('sort_by'),
                    sort_order=sort_params.get('sort_order'),
                    db_session=db_session
                )

                tasks = sort_result["tasks"]

                if not tasks:
                    return "You have no tasks."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                sort_description = sort_params.get('sort_by', 'default')
                return f"Here are your tasks ordered by {sort_description} ({len(tasks)} total):\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error ordering tasks: {str(e)}")
                return "Sorry, I couldn't order your tasks. Please try again."

        # NEW: Pattern for "what's due tomorrow" → filter_tasks with date filter
        due_tomorrow_match = re.search(r"^(?:what'?s|what are|show me)\s+(?:due\s+)?tomorrow$", user_message.strip(), re.IGNORECASE)
        if due_tomorrow_match:
            from datetime import datetime, timedelta
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow_str = tomorrow.strftime('%Y-%m-%d')

            try:
                # Use filter_tasks function with date filter for tomorrow
                filter_result = await filter_tasks(
                    user_id=user_id,
                    date_from=tomorrow_str,
                    date_to=tomorrow_str,
                    completed=False,  # Only incomplete tasks
                    db_session=db_session
                )

                tasks = filter_result["tasks"]

                if not tasks:
                    return f"No tasks are due tomorrow ({tomorrow_str})."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Here are your tasks due tomorrow ({tomorrow_str}) ({len(tasks)} total):\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error filtering tasks by due date: {str(e)}")
                return "Sorry, I couldn't filter your tasks by due date. Please try again."

        # NEW: Pattern for "Show only high priority tasks" → filter_tasks
        show_only_high_priority_match = re.search(r'^show only (.+?) priority tasks$', user_message.strip(), re.IGNORECASE)
        if show_only_high_priority_match:
            priority = show_only_high_priority_match.group(1).strip()

            # Validate that the priority is valid
            valid_priorities = ['high', 'medium', 'low']
            if priority.lower() in valid_priorities:
                try:
                    # Use filter_tasks function with priority
                    filter_result = await filter_tasks(
                        user_id=user_id,
                        priority=[priority.lower()],  # Note: filter_tasks expects a list
                        db_session=db_session
                    )

                    tasks = filter_result["tasks"]

                    if not tasks:
                        return f"No {priority} priority tasks found."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "HIGH "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "MED "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "LOW "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"[DONE] {task_entry}"
                        else:
                            task_entry = f"[TODO] {task_entry}"
                        task_list.append(task_entry)

                    return f"Here are your {priority} priority tasks ({len(tasks)} total):\n" + "\n".join(task_list)
                except Exception as e:
                    logger.error(f"Error filtering tasks by priority: {str(e)}")
                    return "Sorry, I couldn't filter your tasks by priority. Please try again."

        # NEW: Pattern for "Set task X as medium priority" → update_task
        set_task_priority_match = re.search(r'^set task (.+?) as (high|medium|low) priority$', user_message.strip(), re.IGNORECASE)
        if set_task_priority_match:
            task_title = set_task_priority_match.group(1).strip()
            priority = set_task_priority_match.group(2).strip()

            # Validate priority
            valid_priorities = ['high', 'medium', 'low']
            if priority.lower() not in valid_priorities:
                return f"'{priority}' is not a valid priority. Please use high, medium, or low."

            try:
                # Find tasks by title (there might be multiple with the same title)
                list_result = await list_tasks(user_id=user_id, db_session=db_session)
                tasks = list_result["tasks"]

                matching_tasks = []
                for task in tasks:
                    if task_title.lower() in task["title"].lower() or task["title"].lower() in task_title.lower():
                        matching_tasks.append(task)

                if not matching_tasks:
                    return f"No tasks found matching '{task_title}'."
                elif len(matching_tasks) > 1:
                    return f"Multiple tasks match '{task_title}'. Please be more specific or use the task number."
                else:
                    task = matching_tasks[0]
                    # Update the task with the new priority
                    result = await update_task(
                        task_id=task["id"],
                        user_id=user_id,
                        title=task["title"],
                        completed=task["completed"],
                        priority=priority.lower(),
                        category=task.get("category"),
                        tags=task.get("tags"),
                        db_session=db_session
                    )

                    return f"Task '{task['title']}' has been set to {priority} priority."
            except Exception as e:
                logger.error(f"Error updating task priority: {str(e)}")
                return f"Sorry, I couldn't update the task priority. Error: {str(e)}"

        # NEW: Pattern for "Search for meeting in my tasks" → filter_tasks
        search_tasks_match = re.search(r'^search for (.+?) in my tasks$', user_message.strip(), re.IGNORECASE)
        if search_tasks_match:
            search_term = search_tasks_match.group(1).strip()

            try:
                # Get all tasks
                list_result = await list_tasks(user_id=user_id, db_session=db_session)
                tasks = list_result["tasks"]

                # Filter tasks that contain the search term
                matching_tasks = []
                for task in tasks:
                    if search_term.lower() in task["title"].lower():
                        matching_tasks.append(task)

                if not matching_tasks:
                    return f"No tasks found containing '{search_term}'."

                # Format matching tasks for display
                task_list = []
                for i, task in enumerate(matching_tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Found {len(matching_tasks)} task(s) containing '{search_term}':\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error searching tasks: {str(e)}")
                return f"Sorry, I couldn't search your tasks. Error: {str(e)}"

        # NEW: Pattern for "I need to remember to X" → add_task
        remember_task_match = re.search(r'^i need to remember to (.+)$', user_message.strip(), re.IGNORECASE)
        if remember_task_match:
            title = remember_task_match.group(1).strip()

            try:
                # Create task
                result = await add_task(
                    user_id=user_id,
                    title=title,
                    db_session=db_session
                )

                return f"I've added '{title}' to your tasks so you won't forget."
            except Exception as e:
                logger.error(f"Error adding remember task: {str(e)}")
                return f"Sorry, I couldn't add the task. Error: {str(e)}"

        # NEW: Pattern for "What tasks do I have?" → list_tasks
        what_tasks_match = re.search(r'^what tasks do i have\??$', user_message.strip(), re.IGNORECASE)
        if what_tasks_match:
            try:
                # Use list_tasks function to get all tasks
                result = await list_tasks(user_id=user_id, db_session=db_session)
                tasks = result["tasks"]

                if not tasks:
                    return "You don't have any tasks yet."

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"You have {len(tasks)} task(s):\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error listing tasks: {str(e)}")
                return "Sorry, I couldn't retrieve your tasks. Please try again."

        # NEW: Pattern for "Task X is completed" → complete_task
        task_completed_match = re.search(r'^(?:task )(.+?) is completed$', user_message.strip(), re.IGNORECASE)
        if task_completed_match:
            task_title = task_completed_match.group(1).strip()

            try:
                # Find tasks by title (there might be multiple with the same title)
                list_result = await list_tasks(user_id=user_id, db_session=db_session)
                tasks = list_result["tasks"]

                matching_tasks = []
                for task in tasks:
                    if task_title.lower() in task["title"].lower() or task["title"].lower() in task_title.lower():
                        matching_tasks.append(task)

                if not matching_tasks:
                    return f"No tasks found matching '{task_title}'."
                elif len(matching_tasks) > 1:
                    return f"Multiple tasks match '{task_title}'. Please be more specific or use the task number."
                else:
                    task = matching_tasks[0]
                    # Complete the task
                    result = await complete_task(
                        task_id=task["id"],
                        user_id=user_id,
                        db_session=db_session
                    )

                    return f"Task '{task['title']}' has been marked as completed."
            except Exception as e:
                logger.error(f"Error completing task: {str(e)}")
                return f"Sorry, I couldn't complete the task. Error: {str(e)}"

        # NEW: Pattern for "Cancel task X" → delete_task
        cancel_task_match = re.search(r'^cancel task (.+)$', user_message.strip())
        if cancel_task_match:
            task_title = cancel_task_match.group(1).strip()

            try:
                # Find tasks by title (there might be multiple with the same title)
                list_result = await list_tasks(user_id=user_id, db_session=db_session)
                tasks = list_result["tasks"]

                matching_tasks = []
                for task in tasks:
                    if task_title.lower() in task["title"].lower() or task["title"].lower() in task_title.lower():
                        matching_tasks.append(task)

                if not matching_tasks:
                    return f"No tasks found matching '{task_title}'."
                elif len(matching_tasks) > 1:
                    return f"Multiple tasks match '{task_title}'. Please be more specific or use the task number."
                else:
                    task = matching_tasks[0]
                    # Delete the task
                    result = await delete_task(
                        task_id=task["id"],
                        user_id=user_id,
                        db_session=db_session
                    )

                    return f"Task '{task['title']}' has been cancelled and removed."
            except Exception as e:
                logger.error(f"Error cancelling task: {str(e)}")
                return f"Sorry, I couldn't cancel the task. Error: {str(e)}"

        # NEW: Pattern for "Rename task X to Y" → update_task
        rename_task_match = re.search(r'^rename task (.+?) to (.+)$', user_message.strip())
        if rename_task_match:
            old_title = rename_task_match.group(1).strip()
            new_title = rename_task_match.group(2).strip()

            try:
                # Find tasks by title (there might be multiple with the same title)
                list_result = await list_tasks(user_id=user_id, db_session=db_session)
                tasks = list_result["tasks"]

                matching_tasks = []
                for task in tasks:
                    if old_title.lower() in task["title"].lower() or task["title"].lower() in old_title.lower():
                        matching_tasks.append(task)

                if not matching_tasks:
                    return f"No tasks found matching '{old_title}'."
                elif len(matching_tasks) > 1:
                    return f"Multiple tasks match '{old_title}'. Please be more specific or use the task number."
                else:
                    task = matching_tasks[0]
                    # Update the task with the new title
                    result = await update_task(
                        task_id=task["id"],
                        user_id=user_id,
                        title=new_title,
                        completed=task["completed"],
                        priority=task.get("priority"),
                        category=task.get("category"),
                        tags=task.get("tags"),
                        db_session=db_session
                    )

                    return f"Task '{task['title']}' has been renamed to '{new_title}'."
            except Exception as e:
                logger.error(f"Error renaming task: {str(e)}")
                return f"Sorry, I couldn't rename the task. Error: {str(e)}"

        # NEW: Pattern for "Make task X Y priority" → update_task
        make_task_priority_match = re.search(r'^make task (.+?) (high|medium|low) priority$', user_message.strip(), re.IGNORECASE)
        if make_task_priority_match:
            task_title = make_task_priority_match.group(1).strip()
            priority = make_task_priority_match.group(2).strip()

            # Validate priority
            valid_priorities = ['high', 'medium', 'low']
            if priority.lower() not in valid_priorities:
                return f"'{priority}' is not a valid priority. Please use high, medium, or low."

            try:
                # Find tasks by title (there might be multiple with the same title)
                list_result = await list_tasks(user_id=user_id, db_session=db_session)
                tasks = list_result["tasks"]

                matching_tasks = []
                for task in tasks:
                    if task_title.lower() in task["title"].lower() or task["title"].lower() in task_title.lower():
                        matching_tasks.append(task)

                if not matching_tasks:
                    return f"No tasks found matching '{task_title}'."
                elif len(matching_tasks) > 1:
                    return f"Multiple tasks match '{task_title}'. Please be more specific or use the task number."
                else:
                    task = matching_tasks[0]
                    # Update the task with the new priority
                    result = await update_task(
                        task_id=task["id"],
                        user_id=user_id,
                        title=task["title"],
                        completed=task["completed"],
                        priority=priority.lower(),
                        category=task.get("category"),
                        tags=task.get("tags"),
                        db_session=db_session
                    )

                    return f"Task '{task['title']}' has been set to {priority} priority."
            except Exception as e:
                logger.error(f"Error updating task priority: {str(e)}")
                return f"Sorry, I couldn't update the task priority. Error: {str(e)}"

        # NEW: Pattern for "Arrange by creation date" → list_tasks with sort parameters
        arrange_by_date_match = re.search(r'^arrange by (creation|created) date$', user_message.strip(), re.IGNORECASE)
        if arrange_by_date_match:
            try:
                # Use list_tasks function to get all tasks, sorted by creation date
                # Since the list_tasks function doesn't have sorting capability yet, we'll fetch and sort manually
                result = await list_tasks(user_id=user_id, db_session=db_session)
                tasks = result["tasks"]

                if not tasks:
                    return "You don't have any tasks yet."

                # Sort tasks by creation date (assuming they have created_at field)
                # Sort by created_at field (newest first for creation date arrangement)
                tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)

                # Format tasks for display
                task_list = []
                for i, task in enumerate(tasks, 1):
                    # Get priority indicator
                    priority_indicator = ""
                    if task.get("priority"):
                        if task["priority"].lower() == "high":
                            priority_indicator = "HIGH "
                        elif task["priority"].lower() == "medium":
                            priority_indicator = "MED "
                        elif task["priority"].lower() == "low":
                            priority_indicator = "LOW "

                    # Get tags
                    tags_display = ""
                    if task.get("tags"):
                        try:
                            import json
                            tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                            if tags:
                                tags_display = f" #{' #'.join(tags)}"
                        except:
                            pass

                    task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                    if task.get("completed"):
                        task_entry = f"[DONE] {task_entry}"
                    else:
                        task_entry = f"[TODO] {task_entry}"
                    task_list.append(task_entry)

                return f"Here are your tasks arranged by creation date (newest first) ({len(tasks)} total):\n" + "\n".join(task_list)
            except Exception as e:
                logger.error(f"Error arranging tasks by date: {str(e)}")
                return "Sorry, I couldn't arrange your tasks by creation date. Please try again."

        # DEBUG: Add a print to see if we reach the fallback
        print(f"DEBUG: No pattern matched for message: '{user_message}'. Falling back to mock response.")

        # If none of the above patterns match, use fallback response
        # For now, we'll call the mock AI response as a fallback
        return await mock_ai_response(user_message)
    except Exception as e:
        logger.error(f"Error in invoke_agent: {str(e)}")
        return f"Sorry, I encountered an error processing your request: {str(e)}"


def extract_task_title(message: str) -> str:
    """
    Extract task title from natural language message
    This is a simple implementation - in a real system, this would use NLP/ML
    """
    # Remove surrounding quotes FIRST
    message = message.strip('"\'').strip()

    # For "add task to buy groceries", return "buy groceries"
    # NOT "add task to buy groceries"
    if message.startswith('add task to '):
        return message[12:]  # Remove "add task to "
    return message


def extract_task_title_to_complete(message: str) -> str:
    """
    Extract task title to complete from natural language message
    This is a simple implementation - in a real system, this would use NLP/ML
    Updated to fix numbered task matching inconsistencies
    """
    message = message.strip()
    message_lower = message.lower()

    # Check for numbered task completion patterns first (e.g., "complete task 1", "complete #1", "complete task number 1", "mark task 1 as complete")
    # This pattern captures "task 1", "task #1", "task number 1", "#1", etc.
    number_patterns = [
        r'(?:complete|finish|done|mark as complete|mark as done|mark)\s+(?:task\s+)?(?:number\s+|#)?(\d+)(?:\s+as\s+(?:complete|done))?',
        r'(?:complete|finish|done|mark as complete|mark as done|mark)\s+(?:the\s+|a\s+|an\s+)?task\s+(\d+)',
        r'(?:complete|finish|done|mark as complete|mark as done|mark)\s+(\d+)(?:\s+as\s+(?:complete|done))?'
    ]

    for pattern in number_patterns:
        number_match = re.search(pattern, message_lower)
        if number_match:
            return number_match.group(1)  # Just return the number

    # Special handling for phrases like "Finish the groceries task" -> "groceries"
    # This pattern looks for verbs like finish/complete followed by article and some words before "task"
    special_pattern = re.search(r'(?:complete|finish|done|mark as done|mark as complete)\s+(?:the\s+|a\s+|an\s+)?(.+?)\s+task', message_lower)
    if special_pattern:
        extracted = special_pattern.group(1).strip()
        # Remove common words like "the", "a", "an" from the extracted phrase
        extracted = re.sub(r'\b(the|a|an)\b\s*', '', extracted).strip()
        return extracted

    # Remove common task completion phrases
    prefixes = [
        "complete task: ",
        "complete task ",
        "complete a task: ",
        "complete a task ",
        "finish task: ",
        "finish task ",
        "finish a task: ",
        "finish a task ",
        "mark task: ",
        "mark task ",  # This can conflict with numbered tasks, so we'll handle it specially
        "mark as complete: ",
        "mark as complete ",
        "done with ",
        "completed task: ",
        "completed task ",
        "finish ",
        "complete ",
        "done ",
        "mark "
    ]

    for prefix in prefixes:
        if message_lower.startswith(prefix):
            extracted = message[len(prefix):].strip()

            # Special handling: if the extracted part starts with a number followed by space,
            # it might be a numbered reference (e.g., "1 as complete" from "mark task 1 as complete")
            # Don't return immediately if it looks like a numbered reference
            extracted_lower = extracted.lower()
            if prefix in ["mark task ", "complete task ", "finish task "] and extracted_lower.startswith(('1 ', '2 ', '3 ', '4 ', '5 ', '6 ', '7 ', '8 ', '9 ', '0 ')):
                # This might be a numbered reference, let the numbered pattern matching handle it
                continue

            # Remove common articles and "task" from the end
            extracted = re.sub(r'\b(task|the|a|an)$', '', extracted).strip()
            return extracted

    # If no prefix matches, return the full message as the task to complete
    return message


def extract_task_details_for_update(message: str):
    """
    Extract task title and new details from natural language message for updating tasks
    This is a simple implementation - in a real system, this would use NLP/ML
    Returns a tuple of (task_to_update, new_title, new_description) or (None, None, None)
    """
    message = message.strip()
    message_lower = message.lower()

    # NEW: Handle tag management commands first
    # Pattern for "add [tag_name] tag to task [number]" (e.g., "add urgent tag to task 1", "add work tag to task 2")
    add_tag_pattern = r"add\s+(\w+)\s+tag\s+to\s+task\s+(\d+)"
    add_tag_match = re.search(add_tag_pattern, message_lower)
    if add_tag_match:
        tag_to_add = add_tag_match.group(1).strip()
        task_number = add_tag_match.group(2).strip()
        # Return special format indicating tag operation
        return f"{task_number}_add_tag_{tag_to_add}", None, None

    # Pattern for "remove [tag_name] tag from task [number]" (e.g., "remove urgent tag from task 1", "remove work tag from task 2")
    remove_tag_pattern = r"remove\s+(\w+)\s+tag\s+from\s+task\s+(\d+)"
    remove_tag_match = re.search(remove_tag_pattern, message_lower)
    if remove_tag_match:
        tag_to_remove = remove_tag_match.group(1).strip()
        task_number = remove_tag_match.group(2).strip()
        # Return special format indicating tag removal operation
        return f"{task_number}_remove_tag_{tag_to_remove}", None, None

    # Pattern for numbered task updates (e.g., "update task 1 to buy organic groceries")
    number_pattern = r"(?:update|change|modify)\s+(?:task\s+)?(?:number\s+|#)?(\d+)\s+to\s+(.+)"
    number_match = re.search(number_pattern, message_lower)
    if number_match:
        task_number = number_match.group(1).strip()
        new_details = number_match.group(2).strip()
        # Return the task number as a string to be handled by the task matching logic
        return task_number, new_details, None

    # Look for patterns like "change X to Y", "update X to Y", "modify X to Y"
    # where X is the current task and Y is the new information

    # Pattern 1: "change 'current task' to 'new title'"
    pattern1 = r"change ['\"](.+?)['\"] to ['\"](.+?)['\"]"
    match1 = re.search(pattern1, message_lower)
    if match1:
        current_task = match1.group(1).strip()
        new_title = match1.group(2).strip()
        return current_task, new_title, None

    # Pattern 2: "update 'current task' to 'new title'"
    pattern2 = r"update ['\"](.+?)['\"] to ['\"](.+?)['\"]"
    match2 = re.search(pattern2, message_lower)
    if match2:
        current_task = match2.group(1).strip()
        new_title = match2.group(2).strip()
        return current_task, new_title, None

    # Pattern 3: "modify 'current task' to 'new title'"
    pattern3 = r"modify ['\"](.+?)['\"] to ['\"](.+?)['\"]"
    match3 = re.search(pattern3, message_lower)
    if match3:
        current_task = match3.group(1).strip()
        new_title = match3.group(2).strip()
        return current_task, new_title, None

    # Pattern 4: More general patterns like "change buy groceries to buy organic groceries"
    # Look for phrases like "change X to Y" without quotes
    pattern4 = r"change (.+?) to (.+)"
    match4 = re.search(pattern4, message_lower)
    if match4:
        current_task = match4.group(1).strip()
        new_title = match4.group(2).strip()
        return current_task, new_title, None

    # Pattern 5: "update X to Y" without quotes
    pattern5 = r"update (.+?) to (.+)"
    match5 = re.search(pattern5, message_lower)
    if match5:
        current_task = match5.group(1).strip()
        new_title = match5.group(2).strip()
        return current_task, new_title, None

    # Pattern 6: "modify X to Y" without quotes
    pattern6 = r"modify (.+?) to (.+)"
    match6 = re.search(pattern6, message_lower)
    if match6:
        current_task = match6.group(1).strip()
        new_title = match6.group(2).strip()
        return current_task, new_title, None

    # Pattern 7: Update description specifically
    pattern7 = r"update ['\"](.+?)['\"] description to ['\"](.+?)['\"]"
    match7 = re.search(pattern7, message_lower)
    if match7:
        current_task = match7.group(1).strip()
        new_description = match7.group(2).strip()
        return current_task, None, new_description

    # Pattern 8: Update description without quotes
    pattern8 = r"update (.+?) description to (.+)"
    match8 = re.search(pattern8, message_lower)
    if match8:
        current_task = match8.group(1).strip()
        new_description = match8.group(2).strip()
        return current_task, None, new_description

    # Pattern 9: Change both title and description
    pattern9 = r"change ['\"](.+?)['\"] title to ['\"](.+?)['\"] and description to ['\"](.+?)['\"]"
    match9 = re.search(pattern9, message_lower)
    if match9:
        current_task = match9.group(1).strip()
        new_title = match9.group(2).strip()
        new_description = match9.group(3).strip()
        return current_task, new_title, new_description

    # Pattern 10: Update both title and description
    pattern10 = r"update ['\"](.+?)['\"] title to ['\"](.+?)['\"] and description to ['\"](.+?)['\"]"
    match10 = re.search(pattern10, message_lower)
    if match10:
        current_task = match10.group(1).strip()
        new_title = match10.group(2).strip()
        new_description = match10.group(3).strip()
        return current_task, new_title, new_description

    # Pattern 11: Rename task specifically (e.g., "rename buy groceries to buy organic groceries")
    pattern11 = r"rename ['\"](.+?)['\"] to ['\"](.+?)['\"]"
    match11 = re.search(pattern11, message_lower)
    if match11:
        current_task = match11.group(1).strip()
        new_title = match11.group(2).strip()
        return current_task, new_title, None

    # Pattern 12: Rename without quotes (e.g., "rename buy groceries to buy organic groceries")
    pattern12 = r"rename (.+?) to (.+)"
    match12 = re.search(pattern12, message_lower)
    if match12:
        current_task = match12.group(1).strip()
        new_title = match12.group(2).strip()
        return current_task, new_title, None

    # If no patterns match, return None
    return None, None, None


def extract_priority_from_message(message: str) -> Optional[str]:
    """
    Extract priority from natural language message
    Returns priority level (high, medium, low) or None if not found
    """
    message_lower = message.lower()

    # Check for high priority indicators
    if any(indicator in message_lower for indicator in [
        "high priority", "high-priority", "priority high", "important", "urgent",
        "critical", "top priority", "asap", "as soon as possible"
    ]):
        return "high"

    # Check for medium priority indicators
    if any(indicator in message_lower for indicator in [
        "medium priority", "medium-priority", "priority medium", "normal",
        "standard", "regular"
    ]):
        return "medium"

    # Check for low priority indicators
    if any(indicator in message_lower for indicator in [
        "low priority", "low-priority", "priority low", "low importance",
        "not urgent", "whenever", "when possible"
    ]):
        return "low"

    return None


def extract_tags_from_message(message: str) -> Optional[List[str]]:
    """
    Extract tags from natural language message
    Returns a list of tags or None if no tags found
    """
    message_lower = message.lower()

    # Look for various tag patterns in the message
    tag_patterns = [
        r'with tags ([^,.]+)',           # "with tags work, urgent"
        r'tag: ([^,.]+)',               # "tag: work"
        r'tagged with ([^,.]+)',         # "tagged with work"
        r'add tag ([^\s,.]+)',          # "add tag shopping" - capture until space, comma or period
        r'tags ([^,.]+)',               # "tags work, urgent"
        r'label: ([^,.]+)',             # "label: work"
        r'labels ([^,.]+)'              # "labels work, urgent"
    ]

    tags = []
    for pattern in tag_patterns:
        match = re.search(pattern, message_lower)
        if match:
            tag_text = match.group(1).strip()
            # Split tags by commas, semicolons, or ' and ' (with spaces around 'and')
            raw_tags = re.split(r'[,\s]+|;\s*|\s+and\s+', tag_text)
            for raw_tag in raw_tags:
                clean_tag = raw_tag.strip().lower()
                if clean_tag and clean_tag not in tags:
                    # Skip common words that shouldn't be tags
                    if clean_tag not in {'and', 'or', 'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to'}:
                        tags.append(clean_tag)

    return tags if tags else None


def extract_task_details(message: str):
    """
    Extract task title and description from natural language message
    Returns a tuple of (title, description) or (None, None) if no title found
    """
    message = message.strip()
    message_lower = message.lower()

    # Use the extract_task_title function to get the title
    title = extract_task_title(message)

    # For description, we can extract additional context from the message
    # This is a simple implementation - in a real system, this would use NLP/ML
    description = None

    # Look for common patterns that might indicate additional details
    # For example, after "add task to X to Y" or similar structures
    if title:
        # Extract description based on the original message minus the title
        # This is a simplified approach
        if 'to ' in message_lower and title.lower() in message_lower:
            # If the title was extracted from a "to do" pattern, there might not be a separate description
            pass
        else:
            # In a more sophisticated implementation, we'd extract additional context
            # For now, we'll return None for description as the original function seemed to expect
            pass

    return title, description


def extract_task_title_to_delete(message: str) -> str:
    """
    Extract task title to delete from natural language message
    This is a simple implementation - in a real system, this would use NLP/ML
    """
    message = message.strip()
    message_lower = message.lower()

    # Check for numbered task deletion (e.g., "delete task 1", "delete #1", "remove task number 1")
    number_match = re.search(r'(?:delete|remove|erase|cancel)\s+(?:task\s+)?(?:number\s+|#)?(\d+)', message_lower)
    if number_match:
        return number_match.group(1)  # Just return the number, not with # prefix

    # Special handling for phrases like "delete the groceries task" -> "groceries"
    # This pattern looks for verbs like delete/remove followed by article and some words before "task"
    special_pattern = re.search(r'(?:delete|remove|erase|cancel)\s+(?:the\s+|a\s+|an\s+)?(.+?)\s+task', message_lower)
    if special_pattern:
        extracted = special_pattern.group(1).strip()
        # Remove common words like "the", "a", "an" from the extracted phrase
        extracted = re.sub(r'\b(the|a|an)\b\s*', '', extracted).strip()
        return extracted

    # Remove common task deletion phrases
    prefixes = [
        "delete task: ",
        "delete task ",
        "delete a task: ",
        "delete a task ",
        "remove task: ",
        "remove task ",
        "remove a task: ",
        "remove a task ",
        "delete ",
        "remove ",
        "erase ",
        "cancel ",
        "get rid of "
    ]

    for prefix in prefixes:
        if message_lower.startswith(prefix):
            extracted = message[len(prefix):].strip()
            # Remove common articles and "task" from the end
            extracted = re.sub(r'\b(task|the|a|an)$', '', extracted).strip()
            return extracted

    # If no prefix matches, return the full message as the task to delete
    return message


def find_matching_tasks(search_term: str, tasks: List[dict]) -> List[dict]:
    """
    Find tasks that match the search term using fuzzy matching
    Returns a list of matching tasks sorted by relevance
    """
    search_lower = search_term.lower().strip()
    if not search_lower:
        return []

    matches = []

    for task in tasks:
        title_lower = task["title"].lower()

        # Exact match gets highest priority
        if search_lower == title_lower:
            matches.append((task, 100))  # Highest score
        # Exact match with different casing
        elif search_lower == task["title"].lower():
            matches.append((task, 95))
        # Contains the search term
        elif search_lower in title_lower:
            # Higher score if it's a better match
            score = 80 + len(search_lower)  # Bonus for longer matches
            matches.append((task, score))
        # Is contained in the search term (e.g. "buy groceries" when searching "groceries")
        elif title_lower in search_lower:
            matches.append((task, 70))
        # Contains any of the words from search term
        elif any(word in title_lower for word in search_lower.split()):
            word_matches = sum(1 for word in search_lower.split() if word in title_lower)
            score = 60 + (word_matches * 10)  # Higher score for more word matches
            matches.append((task, score))
        # Check for common substrings (fuzzy matching)
        elif has_common_substring(search_lower, title_lower, min_length=2):
            matches.append((task, 40))

    # Sort by score descending
    matches.sort(key=lambda x: x[1], reverse=True)

    # Return just the task objects, not the scores
    return [task for task, score in matches]


def has_common_substring(str1: str, str2: str, min_length: int = 3) -> bool:
    """
    Check if two strings have a common substring of at least min_length
    """
    if len(str1) < min_length or len(str2) < min_length:
        return False

    # Check all possible substrings of str1 with length >= min_length
    for i in range(len(str1) - min_length + 1):
        for j in range(i + min_length, len(str1) + 1):
            substring = str1[i:j]
            if substring in str2:
                return True
    return False


def extract_task_details_with_priority_and_tags(message: str):
    """
    Extract task title, priority, and tags from natural language message
    Returns a tuple of (title, priority, tags) or (None, None, None) if no title found
    """
    original_message = message
    message = message.strip()
    message_lower = message.lower()

    # Initialize default values
    priority = None
    tags = []

    # Extract priority from message
    priority_keywords = {
        "high": ["high priority", "high-priority", "priority high", "important", "urgent", "critical", "top priority"],
        "medium": ["medium priority", "medium-priority", "priority medium", "normal", "standard", "regular"],
        "low": ["low priority", "low-priority", "priority low", "low importance", "not urgent"]
    }

    for priority_level, keywords in priority_keywords.items():
        for keyword in keywords:
            if keyword in message_lower:
                priority = priority_level
                # Remove the priority keyword from the message to avoid confusion with title
                message_lower = message_lower.replace(keyword, "")
                message = message.replace(keyword, "")

    # Extract tags from message FIRST before processing prefixes
    # Look for tags in various formats: "with tags X", "tag: X", "tagged with X", etc.
    tag_patterns = [
        r'with tags ([^,.]+)',           # "with tags work, urgent"
        r'tag: ([^,.]+)',               # "tag: work"
        r'tagged with ([^,.]+)',        # "tagged with work"
        r'add tag ([^\s,.]+)',          # "add tag shopping" - capture until space, comma or period
        r'tags ([^,.]+)',               # "tags work, urgent"
        r'label: ([^,.]+)',             # "label: work"
        r'labels ([^,.]+)'              # "labels work, urgent"
    ]

    for pattern in tag_patterns:
        match = re.search(pattern, message_lower)
        if match:
            tag_text = match.group(1).strip()
            # Split tags by commas, semicolons, or ' and ' (with spaces around 'and')
            raw_tags = re.split(r'[,\s]+|;\s*|\s+and\s+', tag_text)
            for raw_tag in raw_tags:
                clean_tag = raw_tag.strip().lower()
                if clean_tag and clean_tag not in tags:
                    # Skip common words that shouldn't be tags
                    if clean_tag not in {'and', 'or', 'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to'}:
                        tags.append(clean_tag)
            # Remove the tag pattern from the message to avoid confusion with title
            message = re.sub(pattern, '', message, flags=re.IGNORECASE)
            message_lower = message.lower()  # Update lower case version after replacement

    # Special case: Handle "Add work task" where "work" is meant as a tag
    # Check if the message follows the pattern "add [tag] task"
    add_tag_pattern = r'add\s+(\w+)\s+task$'
    add_match = re.search(add_tag_pattern, message_lower)
    if add_match and not tags:  # Only if no other tags were found
        potential_tag = add_match.group(1)
        # Check if this potential tag is a common tag word (not likely to be the task title)
        common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly'}
        if potential_tag in common_tags:
            tags.append(potential_tag)
            # Remove the tag AND the "task" part from the message to extract the rest as title
            # For "Add work task", we want to remove both "work" and "task" to get a clean message
            message = re.sub(r'\b' + potential_tag + r'\b', '', message, flags=re.IGNORECASE)
            message = re.sub(r'\btask\b', '', message, flags=re.IGNORECASE)  # Remove "task" which is part of command structure
            message = re.sub(r'\badd\s+', '', message, flags=re.IGNORECASE)  # Remove "add" too
            message = message.strip()
            message_lower = message.lower()

    # Remove common task creation phrases to extract the title
    prefixes = [
        "add task to ",
        "add a task to ",
        "create task to ",
        "create a task to ",
        "add task ",
        "add ",
        "create task ",
        "create ",
        "new task ",
        "remember to ",
        "need to ",
        "have to ",
        "should ",
        "add high priority task ",
        "add low priority task ",
        "add medium priority task "
    ]

    # Sort prefixes by length in descending order to match most specific first
    prefixes = sorted(prefixes, key=len, reverse=True)

    title = None
    for prefix in prefixes:
        if message_lower.startswith(prefix):
            title = message[len(prefix):].strip()
            break

    # If no prefix matches, try to extract title by removing priority indicators
    if title is None:
        # Clean up the message and extract the title
        # Remove leading/trailing whitespace and punctuation
        title = message.strip(' .,!?')

    # SPECIAL CASE: If we have tags but no title, and the original message was like "add tag X",
    # then the tag itself should be the title
    if not title and tags and "add tag " in original_message.lower():
        # For "add tag shopping", the title should be "shopping" (the tag)
        if tags:
            title = tags[0]  # Use the first tag as title if no other title was found

    # If title is still None or empty but we have tags, we can return the tags with a title based on tags
    if not title or title.strip() == "":
        if tags:  # If we have tags but no title, create a title based on the tags
            # Use the first tag as the basis for the title if we don't have a meaningful title
            first_tag = tags[0]
            title = f"Task for {first_tag}"
        else:
            return None, None, None

    title = title.strip()

    # If we have tags, remove them from the title to avoid duplication
    # But don't remove them if the title is exactly the same as a tag (special case)
    if tags and title:
        title_lower = title.lower()

        for tag in tags:
            # Only remove tag from title if title is not exactly the tag
            if title_lower != tag.lower():
                title_lower = title_lower.replace(tag.lower(), "")

        title = title_lower.strip(' .,!?').strip()

    return title, priority, tags if tags else None


def extract_priority_filter(message_lower: str) -> Optional[List[str]]:
    """
    Extract priority filter from message
    Returns a list of priorities to filter by
    """
    print(f"DEBUG: extract_priority_filter called with message: '{message_lower}'")

    # NEW: Handle combined filter pattern like "filter by tag work and priority high"
    combined_filter_pattern = r'filter by tag \w+ and priority (\w+)'
    combined_match = re.search(combined_filter_pattern, message_lower)
    if combined_match:
        priority_word = combined_match.group(1)
        if priority_word in ['high', 'medium', 'low']:
            print(f"DEBUG: Found combined filter priority: {priority_word}")
            return [priority_word]

    # Check for priority filters like "filter by high priority", "show high priority tasks", etc.
    # Also handle combined filters like "filter by tag work and priority high"
    if "high priority" in message_lower or "high-priority" in message_lower or "priority high" in message_lower:
        print("DEBUG: Found 'high priority' pattern")
        return ["high"]
    elif "medium priority" in message_lower or "medium-priority" in message_lower or "priority medium" in message_lower:
        print("DEBUG: Found 'medium priority' pattern")
        return ["medium"]
    elif "low priority" in message_lower or "low-priority" in message_lower or "priority low" in message_lower:
        print("DEBUG: Found 'low priority' pattern")
        return ["low"]
    elif any(phrase in message_lower for phrase in [
        "important", "urgent", "critical", "top priority"
    ]) and ("filter by" in message_lower or "show" in message_lower):
        print("DEBUG: Found important/urgent pattern with filter/show")
        return ["high"]
    elif any(phrase in message_lower for phrase in [
        "normal", "standard", "regular"
    ]) and ("filter by" in message_lower or "show" in message_lower):
        print("DEBUG: Found normal/standard pattern with filter/show")
        return ["medium"]
    elif any(phrase in message_lower for phrase in [
        "low importance", "not urgent"
    ]) and ("filter by" in message_lower or "show" in message_lower):
        print("DEBUG: Found low importance pattern with filter/show")
        return ["low"]

    # Check for direct priority requests like "high priority tasks"
    if any(phrase in message_lower for phrase in [
        "high priority tasks", "high-priority tasks", "important tasks", "urgent tasks"
    ]):
        print("DEBUG: Found high priority tasks pattern")
        return ["high"]
    elif any(phrase in message_lower for phrase in [
        "medium priority tasks", "medium-priority tasks", "normal tasks", "standard tasks"
    ]):
        print("DEBUG: Found medium priority tasks pattern")
        return ["medium"]
    elif any(phrase in message_lower for phrase in [
        "low priority tasks", "low-priority tasks", "low importance tasks"
    ]):
        print("DEBUG: Found low priority tasks pattern")
        return ["low"]

    print("DEBUG: No priority filter found")
    return None


def extract_due_date(message_lower: str) -> Optional[str]:
    """
    Extract due date from message
    Returns a date string in ISO format or None if no date found
    """
    from datetime import datetime, timedelta
    import re

    # Normalize the message for date extraction
    message_normalized = message_lower.strip()

    # Handle relative dates
    if "tomorrow" in message_normalized:
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.strftime('%Y-%m-%d')

    if "today" in message_normalized:
        today = datetime.now()
        return today.strftime('%Y-%m-%d')

    if "this week" in message_normalized:
        # Return the start of the current week (Monday)
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())  # Monday of current week
        return start_of_week.strftime('%Y-%m-%d')
    elif "next week" in message_normalized:
        next_week = datetime.now() + timedelta(weeks=1)
        return next_week.strftime('%Y-%m-%d')

    if "next month" in message_normalized:
        # Add approximately one month (30 days)
        next_month = datetime.now() + timedelta(days=30)
        return next_month.strftime('%Y-%m-%d')

    if "in 2 days" in message_normalized or "in two days" in message_normalized:
        in_two_days = datetime.now() + timedelta(days=2)
        return in_two_days.strftime('%Y-%m-%d')

    if "in 3 days" in message_normalized or "in three days" in message_normalized:
        in_three_days = datetime.now() + timedelta(days=3)
        return in_three_days.strftime('%Y-%m-%d')

    # Handle specific days of the week
    days_of_week = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }

    for day, day_num in days_of_week.items():
        if day in message_normalized:
            today = datetime.now()
            days_ahead = day_num - today.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            next_day = today + timedelta(days=days_ahead)
            return next_day.strftime('%Y-%m-%d')

    # Handle specific date formats (e.g., "due Jan 22", "deadline 22 Jan", etc.)
    date_patterns = [
        r'due\s+(\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?)',  # due 01/22 or due 01-22
        r'due\s+(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*)',  # due 22 Jan
        r'deadline\s+(\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?)',  # deadline 01/22
        r'deadline\s+(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*)',  # deadline 22 Jan
        r'on\s+(\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?)',  # on 01/22
        r'on\s+(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*)',  # on 22 Jan
    ]

    for pattern in date_patterns:
        match = re.search(pattern, message_normalized)
        if match:
            date_str = match.group(1)
            # Try to parse the date string
            try:
                # Handle different date formats
                if '/' in date_str or '-' in date_str:
                    parts = date_str.split('/')
                    if len(parts) == 2:
                        # Assume MM/DD format and add current year
                        month, day = parts
                        current_year = datetime.now().year
                        parsed_date = datetime.strptime(f"{month}/{day}/{current_year}", "%m/%d/%Y")
                    elif len(parts) == 3:
                        # Could be MM/DD/YYYY or DD/MM/YYYY - assume MM/DD/YYYY
                        month, day, year = parts
                        if len(year) == 2:
                            year = f"20{year}"  # Convert 22 to 2022
                        parsed_date = datetime.strptime(f"{month}/{day}/{year}", "%m/%d/%Y")
                    else:
                        continue
                else:
                    # Handle "22 Jan" format
                    try:
                        # Try different formats
                        parsed_date = datetime.strptime(date_str, "%d %B")  # 22 January
                        current_year = datetime.now().year
                        # Recreate with current year
                        parsed_date = datetime(current_year, parsed_date.month, parsed_date.day)
                    except ValueError:
                        try:
                            parsed_date = datetime.strptime(date_str, "%d %b")  # 22 Jan
                            current_year = datetime.now().year
                            # Recreate with current year
                            parsed_date = datetime(current_year, parsed_date.month, parsed_date.day)
                        except ValueError:
                            continue

                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue

    return None


def extract_tags_filter(message_lower: str) -> Optional[List[str]]:
    """
    Extract tags filter from message
    Returns a list of tags to filter by
    """
    # NEW: Handle combined filter pattern like "filter by tag work and priority high"
    combined_filter_pattern = r'filter by tag (\w+)(?: and priority \w+)?'
    combined_match = re.search(combined_filter_pattern, message_lower)
    if combined_match:
        potential_tag = combined_match.group(1)
        common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly', 'private', 'business'}
        if potential_tag in common_tags:
            return [potential_tag]

    # Look for tag patterns in filtering/searching contexts
    tag_patterns = [
        r'with tags ([^,.]+)',           # "with tags work, urgent"
        r'tag: ([^,.]+)',               # "tag: work"
        r'tagged with ([^,.]+)',         # "tagged with work"
        r'tags ([^,.]+)',               # "tags work, urgent"
        r'labeled ([^,.]+)',            # "labeled work"
        r'label: ([^,.]+)',             # "label: work"
        r'labels ([^,.]+)',             # "labels work, urgent"
        r'filter by tag ([^,.]+)',       # "filter by tag shopping" - NEW PATTERN
        r'filter by tags ([^,.]+)',      # "filter by tags work, urgent" - NEW PATTERN
        r'filter tasks? by tag ([^,.]+)', # "filter task by tag work" or "filter tasks by tag work"
    ]

    for pattern in tag_patterns:
        match = re.search(pattern, message_lower)
        if match:
            tag_text = match.group(1).strip()
            # Split tags by commas, semicolons, or ' and ' (with spaces around 'and')
            raw_tags = re.split(r'[,\s]+|;\s*|\s+and\s+', tag_text)
            tags = []
            for raw_tag in raw_tags:
                clean_tag = raw_tag.strip().lower()
                if clean_tag and clean_tag not in tags:
                    # Skip common words that shouldn't be tags
                    if clean_tag not in {'and', 'or', 'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to'}:
                        tags.append(clean_tag)
            return tags if tags else None

    # Handle specific patterns for "show [tag] tasks" and "find [tag] items"
    # Look for patterns like "show work tasks" or "find shopping items"
    show_pattern = re.search(r'show (\w+) tasks', message_lower)
    if show_pattern:
        potential_tag = show_pattern.group(1)
        # Only return if it's a common tag word
        common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly', 'private', 'business'}
        if potential_tag in common_tags:
            return [potential_tag]

    # Handle "show tasks with [tag] tag" pattern
    show_with_tag_pattern = re.search(r'show tasks with (\w+) tag', message_lower)
    if show_with_tag_pattern:
        potential_tag = show_with_tag_pattern.group(1)
        # Only return if it's a common tag word
        common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly', 'private', 'business'}
        if potential_tag in common_tags:
            return [potential_tag]

    find_pattern = re.search(r'find (\w+) items', message_lower)
    if find_pattern:
        potential_tag = find_pattern.group(1)
        # Only return if it's a common tag word
        common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly', 'private', 'business'}
        if potential_tag in common_tags:
            return [potential_tag]

    # Check for direct tag filtering like "work tasks", "shopping tasks"
    # This is more contextual - look for specific tag mentions
    if "work" in message_lower and any(phrase in message_lower for phrase in [
        "filter by", "show", "tasks with", "tasks tagged", "search for", "find"
    ]):
        # Check if "work" refers to a tag in this context
        if any(phrase in message_lower for phrase in [
            "work tasks", "work related tasks", "tasks for work", "work items"
        ]):
            return ["work"]

    if "shopping" in message_lower and any(phrase in message_lower for phrase in [
        "filter by", "show", "tasks with", "tasks tagged", "search for", "find"
    ]):
        if any(phrase in message_lower for phrase in [
            "shopping tasks", "shopping related tasks", "tasks for shopping", "shopping items"
        ]):
            return ["shopping"]

    # Additional context-aware tag detection for common patterns
    if "filter by" in message_lower and ("tag" in message_lower or "tags" in message_lower):
        # Extract potential tag after "filter by tag" or "filter by tags"
        filter_tag_match = re.search(r'filter by tag (\w+)', message_lower)
        if filter_tag_match:
            potential_tag = filter_tag_match.group(1)
            # Only return if it's a common tag word
            common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly', 'private', 'business'}
            if potential_tag in common_tags:
                return [potential_tag]

    return None


def extract_search_term(message_lower: str) -> Optional[str]:
    """
    Extract search term from message
    Returns a search term to search for in tasks
    """
    # Remove extra quotes and clean up the message
    # Handle cases where the message might have trailing quotes
    message_lower = re.sub(r'["\']+$', '', message_lower).strip()  # Remove trailing quotes

    # Look for search patterns
    search_patterns = [
        r'look for ([^,.]+)',           # "look for groceries" - NEW: Added this for requirement
        r'search for ([^,.]+)',         # "search for groceries"
        r'search tasks? with ([^,.]+)', # "search task with groceries"
        r'find tasks? with ([^,.]+)',   # "find tasks with milk" - NEW: Added for requirement
    ]

    for pattern in search_patterns:
        match = re.search(pattern, message_lower)
        if match:
            search_term = match.group(1).strip()
            # Clean up the search term by removing trailing quotes
            search_term = re.sub(r'["\']+$', '', search_term).strip()
            # Clean up the search term
            search_term = re.sub(r'\btask[s]?\b', '', search_term).strip()

            # Special handling: if this looks like a tag-based request (e.g., "find work items"),
            # defer to tag filtering instead of search
            tag_items_match = re.match(r'(\w+)\s+items?$', search_term)
            if tag_items_match:
                potential_tag = tag_items_match.group(1)
                common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly', 'private', 'business'}
                if potential_tag in common_tags:
                    return None  # Let tag filtering handle this

            return search_term if search_term else None

    # Special handling for "find [item]" - exclude "find [tag] items" patterns
    # since those should be handled by tag filtering instead of search
    find_match = re.search(r'find ([^,.]+)', message_lower)
    if find_match:
        find_term = find_match.group(1).strip()
        # Clean up by removing trailing quotes
        find_term = re.sub(r'["\']+$', '', find_term).strip()

        # Check if it's in the format "find [tag] items", defer to tag filtering instead
        tag_items_match = re.match(r'(\w+)\s+items?$', find_term)
        if tag_items_match:
            potential_tag = tag_items_match.group(1)
            # Check if it's a common tag that should be filtered rather than searched
            common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly', 'private', 'business'}
            if potential_tag in common_tags:
                # This is likely a tag-based request, so return None to let tag filtering handle it
                return None
        # Otherwise, treat it as a regular search term
        find_term = re.sub(r'\btask[s]?\b', '', find_term).strip()
        return find_term if find_term else None

    # Also check for "find task with [term]" pattern but not "find [tag] items"
    find_with_match = re.search(r'find tasks? with ([^,.]+)', message_lower)
    if find_with_match:
        search_term = find_with_match.group(1).strip()
        # Clean up by removing trailing quotes
        search_term = re.sub(r'["\']+$', '', search_term).strip()
        search_term = re.sub(r'\btask[s]?\b', '', search_term).strip()
        return search_term if search_term else None

    # Also check for "search for X tasks" pattern
    if "search for" in message_lower:
        # Extract everything between "search for" and "tasks"
        search_match = re.search(r'search for (.+?) tasks?', message_lower)
        if search_match:
            search_term = search_match.group(1).strip()
            # Clean up by removing trailing quotes
            search_term = re.sub(r'["\']+$', '', search_term).strip()
            search_term = re.sub(r'\btask[s]?\b', '', search_term).strip()
            return search_term if search_term else None

    return None


def extract_sort_params(message_lower: str) -> dict:
    """
    Extract sort parameters from message
    Returns a dict with sort_by and sort_order
    """
    sort_params = {}

    # NEW: Handle "Show newest high priority tasks" - extract sort info first
    if "newest" in message_lower and any(phrase in message_lower for phrase in [
        "show", "list", "display", "find"
    ]):
        sort_params['sort_by'] = 'created_at'
        sort_params['sort_order'] = 'desc'  # newest first

    # Check for sort by date/time
    if any(phrase in message_lower for phrase in [
        "sort by date", "sort tasks by date", "sort by created date",
        "sort by time", "sort by created time", "sort by age",
        "sort by newest", "sort by oldest", "sort by creation date"
    ]):
        sort_params['sort_by'] = 'created_at'
        if any(phrase in message_lower for phrase in [
            "newest", "most recent", "latest"
        ]):
            sort_params['sort_order'] = 'desc'
        elif any(phrase in message_lower for phrase in [
            "oldest", "earliest"
        ]):
            sort_params['sort_order'] = 'asc'
        else:
            sort_params['sort_order'] = 'desc'  # Default to newest first

    # Check for sort by priority
    elif any(phrase in message_lower for phrase in [
        "sort by priority", "sort tasks by priority", "sort by importance"
    ]):
        sort_params['sort_by'] = 'priority'
        if "descending" in message_lower or "high to low" in message_lower:
            sort_params['sort_order'] = 'desc'
        else:
            sort_params['sort_order'] = 'asc'

    # Check for sort by title/alphabetical
    elif any(phrase in message_lower for phrase in [
        "sort by title", "sort tasks by title", "sort alphabetically",
        "sort by name", "sort tasks by name"
    ]):
        sort_params['sort_by'] = 'title'
        if "descending" in message_lower or "z to a" in message_lower:
            sort_params['sort_order'] = 'desc'
        else:
            sort_params['sort_order'] = 'asc'

    # Check for sort by completion status
    elif any(phrase in message_lower for phrase in [
        "sort by status", "sort tasks by status", "sort by completion",
        "sort by completed", "sort by pending"
    ]):
        sort_params['sort_by'] = 'completed'
        if "completed first" in message_lower or "done first" in message_lower:
            sort_params['sort_order'] = 'desc'
        else:
            sort_params['sort_order'] = 'asc'

    return sort_params


# Additional agent functionality will be added in future phases