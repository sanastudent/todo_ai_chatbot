"""
Filtering logic for the Todo AI Chatbot.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import and_, or_
from sqlmodel import select

from src.models.task import Task


def apply_multi_criteria_filter(base_query, filters: Dict[str, Any]):
    """
    Apply multiple filter criteria to a base query.

    Args:
        base_query: Base SQLModel query
        filters: Dictionary containing filter criteria

    Returns:
        Modified query with filter conditions applied
    """
    query = base_query

    # Apply completion status filter
    completed = filters.get('completed')
    if completed is not None:
        query = query.where(Task.completed == completed)

    # Apply priority filter
    priority = filters.get('priority')
    if priority:
        if isinstance(priority, list):
            query = query.where(Task.priority.in_(priority))
        else:
            query = query.where(Task.priority == priority)

    # Apply tags filter
    tags = filters.get('tags')
    if tags and isinstance(tags, list):
        for tag in tags:
            query = query.where(Task.tags.like(f'%"{tag}"%'))

    # Apply date range filters
    date_from = filters.get('date_from')
    if date_from:
        query = query.where(Task.created_at >= date_from)

    date_to = filters.get('date_to')
    if date_to:
        query = query.where(Task.created_at <= date_to)

    return query


def validate_combined_filters(filters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate that combined filters are logically consistent.

    Args:
        filters: Dictionary containing filter criteria

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for conflicting date ranges
    date_from = filters.get('date_from')
    date_to = filters.get('date_to')

    if date_from and date_to and date_from > date_to:
        return False, "date_from cannot be after date_to"

    # Validate priority values
    priority = filters.get('priority')
    if priority:
        allowed_priorities = {"high", "medium", "low"}
        if isinstance(priority, list):
            invalid_priorities = [p for p in priority if p not in allowed_priorities]
            if invalid_priorities:
                return False, f"Invalid priority values: {invalid_priorities}"
        elif priority not in allowed_priorities:
            return False, f"Invalid priority value: {priority}"

    # Validate tags format
    tags = filters.get('tags')
    if tags and not isinstance(tags, list):
        return False, "Tags filter must be a list of strings"

    return True, None


def optimize_filter_performance(query, filters: Dict[str, Any]):
    """
    Apply performance optimizations to the query based on filters.

    Args:
        query: SQLModel query to optimize
        filters: Dictionary containing filter criteria

    Returns:
        Optimized query
    """
    # In a real implementation, this would apply specific optimizations
    # based on the types of filters being used
    # For example: adjusting join strategies, hinting indexes, etc.
    return query


def filter_tasks_locally(tasks: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Apply filters to a list of tasks in memory (for post-query filtering).

    Args:
        tasks: List of task dictionaries
        filters: Dictionary containing filter criteria

    Returns:
        Filtered list of task dictionaries
    """
    filtered_tasks = tasks

    # Apply completion status filter
    completed = filters.get('completed')
    if completed is not None:
        filtered_tasks = [task for task in filtered_tasks if task['completed'] == completed]

    # Apply priority filter
    priority = filters.get('priority')
    if priority:
        if isinstance(priority, list):
            filtered_tasks = [task for task in filtered_tasks if task['priority'] in priority]
        else:
            filtered_tasks = [task for task in filtered_tasks if task['priority'] == priority]

    # Apply tags filter
    tags = filters.get('tags')
    if tags and isinstance(tags, list):
        filtered_tasks = [
            task for task in filtered_tasks
            if any(tag in task['tags'] for tag in tags)
        ]

    # Apply date range filters
    date_from = filters.get('date_from')
    if date_from:
        filtered_tasks = [
            task for task in filtered_tasks
            if datetime.fromisoformat(task['created_at']) >= date_from
        ]

    date_to = filters.get('date_to')
    if date_to:
        filtered_tasks = [
            task for task in filtered_tasks
            if datetime.fromisoformat(task['created_at']) <= date_to
        ]

    return filtered_tasks