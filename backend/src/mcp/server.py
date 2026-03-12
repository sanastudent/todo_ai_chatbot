from fastmcp import FastMCP
import asyncio
from typing import Dict, Any, Optional

from src.mcp.tools import add_task, list_tasks, complete_task, update_task, delete_task, filter_tasks, add_task_with_details, get_task_stats, search_tasks, bulk_operations


# Create the FastMCP server instance
mcp_server = FastMCP(
    name="Todo Chatbot MCP Server"
)


@mcp_server.tool(
    "add_task",
    description="Create a new task for the user. Call this when the user wants to add, create, or remember something they need to do."
)
async def add_task_handler(user_id: str, title: str, description: Optional[str] = None, priority: Optional[str] = None, tags: Optional[list] = None) -> Dict[str, Any]:
    """
    MCP tool handler for adding tasks
    """
    # db_session will be created internally by the add_task function
    result = await add_task(
        user_id=user_id,
        title=title,
        description=description,
        priority=priority,
        tags=tags,
        db_session=None  # Let the function create its own session
    )

    return result


@mcp_server.tool(
    "list_tasks",
    description="Retrieve all tasks for the user, optionally filtered by completion status. Call this when the user wants to see, show, list, or view their tasks."
)
async def list_tasks_handler(user_id: str, completed: Optional[bool] = None, priority: Optional[list] = None, tags: Optional[list] = None, search_term: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, sort_by: Optional[str] = None, sort_order: Optional[str] = None, limit: Optional[int] = 50, offset: Optional[int] = 0) -> Dict[str, Any]:
    """
    MCP tool handler for listing tasks
    """
    from datetime import datetime
    # Parse dates if provided
    parsed_date_from = datetime.fromisoformat(date_from) if date_from else None
    parsed_date_to = datetime.fromisoformat(date_to) if date_to else None

    result = await list_tasks(
        user_id=user_id,
        completed=completed,
        priority=priority,
        tags=tags,
        search_term=search_term,
        date_from=parsed_date_from,
        date_to=parsed_date_to,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
        db_session=None  # Let the function create its own session
    )

    return result


@mcp_server.tool(
    "complete_task",
    description="Mark a task as completed. Call this when the user says they finished, completed, or are done with a task."
)
async def complete_task_handler(user_id: str, task_id: str) -> Dict[str, Any]:
    """
    MCP tool handler for completing tasks
    """
    result = await complete_task(
        user_id=user_id,
        task_id=task_id,
        db_session=None  # Let the function create its own session
    )

    return result


@mcp_server.tool(
    "update_task",
    description="Update the title or description of an existing task. Call this when the user wants to modify, change, or update details of a task."
)
async def update_task_handler(user_id: str, task_id: str, title: Optional[str] = None, description: Optional[str] = None, priority: Optional[str] = None, tags: Optional[list] = None) -> Dict[str, Any]:
    """
    MCP tool handler for updating tasks
    """
    result = await update_task(
        user_id=user_id,
        task_id=task_id,
        title=title,
        description=description,
        priority=priority,
        tags=tags,
        db_session=None  # Let the function create its own session
    )

    return result


@mcp_server.tool(
    "delete_task",
    description="Permanently delete a task. Call this when the user wants to remove or delete a task."
)
async def delete_task_handler(user_id: str, task_id: str) -> Dict[str, Any]:
    """
    MCP tool handler for deleting tasks
    """
    result = await delete_task(
        user_id=user_id,
        task_id=task_id,
        db_session=None  # Let the function create its own session
    )

    return result


@mcp_server.tool(
    "filter_tasks",
    description="Filter tasks based on multiple criteria like status, priority, tags, or category. Call this when the user wants to filter, sort, or narrow down their tasks."
)
async def filter_tasks_handler(user_id: str, status: Optional[str] = None, priority: Optional[list] = None, tags: Optional[list] = None, category: Optional[str] = None) -> Dict[str, Any]:
    """
    MCP tool handler for filtering tasks
    """
    result = await filter_tasks(
        user_id=user_id,
        status=status,
        priority=priority,
        tags=tags,
        category=category,
        db_session=None  # Let the function create its own session
    )

    return result


@mcp_server.tool(
    "add_task_with_details",
    description="Create a new task with detailed information including title, description, priority, tags, category, and due date. Call this when the user wants to add a task with comprehensive details."
)
async def add_task_with_details_handler(user_id: str, title: str, description: Optional[str] = None, priority: Optional[str] = None, tags: Optional[list] = None, category: Optional[str] = None, due_date: Optional[str] = None) -> Dict[str, Any]:
    """
    MCP tool handler for adding tasks with details
    """
    result = await add_task_with_details(
        user_id=user_id,
        title=title,
        description=description,
        priority=priority,
        tags=tags,
        category=category,
        due_date=due_date,
        db_session=None  # Let the function create its own session
    )

    return result


@mcp_server.tool(
    "get_task_stats",
    description="Get statistics about user's tasks including totals, completion rates, priority distribution, and common tags. Call this when the user wants to see stats, analytics, or summaries of their tasks."
)
async def get_task_stats_handler(user_id: str, timeframe: Optional[str] = None) -> Dict[str, Any]:
    """
    MCP tool handler for getting task statistics
    """
    result = await get_task_stats(
        user_id=user_id,
        timeframe=timeframe,
        db_session=None  # Let the function create its own session
    )

    return result


@mcp_server.tool(
    "search_tasks",
    description="Search for tasks by keyword across specified fields like title, description, or tags. Call this when the user wants to search, find, or look for specific tasks."
)
async def search_tasks_handler(user_id: str, query: str, search_in: Optional[list] = None) -> Dict[str, Any]:
    """
    MCP tool handler for searching tasks
    """
    result = await search_tasks(
        user_id=user_id,
        query=query,
        search_in=search_in,
        db_session=None  # Let the function create its own session
    )

    return result


@mcp_server.tool(
    "bulk_operations",
    description="Perform bulk operations on multiple tasks like updating priority, status, adding tags, or deleting. Call this when the user wants to perform the same action on multiple tasks at once."
)
async def bulk_operations_handler(user_id: str, operation: str, task_ids: Optional[list] = None, filter_criteria: Optional[dict] = None, new_value: Optional[Any] = None) -> Dict[str, Any]:
    """
    MCP tool handler for bulk operations
    """
    result = await bulk_operations(
        user_id=user_id,
        operation=operation,
        task_ids=task_ids,
        filter_criteria=filter_criteria,
        new_value=new_value,
        db_session=None  # Let the function create its own session
    )

    return result


def get_mcp_tool_functions():
    """
    Return a dictionary mapping tool names to their corresponding functions.
    This allows the OpenAI agent to call these functions directly.
    """
    return {
        "add_task": add_task,
        "list_tasks": list_tasks,
        "complete_task": complete_task,
        "update_task": update_task,
        "delete_task": delete_task,
        "filter_tasks": filter_tasks,
        "add_task_with_details": add_task_with_details,
        "get_task_stats": get_task_stats,
        "search_tasks": search_tasks,
        "bulk_operations": bulk_operations
    }


if __name__ == "__main__":
    # Run the MCP server
    import os

    # Run the FastMCP server using its built-in run method
    mcp_server.run(
        transport="streamable-http",
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_PORT", "3000"))
    )