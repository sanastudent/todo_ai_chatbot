"""
Sorting logic for the Todo AI Chatbot.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime


def apply_custom_priority_sort(tasks: List[Dict[str, Any]], descending: bool = True) -> List[Dict[str, Any]]:
    """
    Sort tasks by priority level (high, medium, low).

    Args:
        tasks: List of task dictionaries
        descending: True to sort high->low priority, False to sort low->high

    Returns:
        Sorted list of task dictionaries
    """
    priority_order = {'high': 1, 'medium': 2, 'low': 3}

    if descending:
        # For descending, we want high priority first, so lower numeric values come first
        sorted_tasks = sorted(tasks, key=lambda x: priority_order.get(x.get('priority', 'medium'), 2))
    else:
        # For ascending, we want low priority first, so higher numeric values come first
        sorted_tasks = sorted(tasks, key=lambda x: priority_order.get(x.get('priority', 'medium'), 2), reverse=True)

    return sorted_tasks


def apply_alphabetical_sort(tasks: List[Dict[str, Any]], descending: bool = False) -> List[Dict[str, Any]]:
    """
    Sort tasks alphabetically by title.

    Args:
        tasks: List of task dictionaries
        descending: True for Z-A, False for A-Z

    Returns:
        Sorted list of task dictionaries
    """
    if descending:
        return sorted(tasks, key=lambda x: x.get('title', '').lower(), reverse=True)
    else:
        return sorted(tasks, key=lambda x: x.get('title', '').lower())


def apply_date_sort(tasks: List[Dict[str, Any]], descending: bool = True) -> List[Dict[str, Any]]:
    """
    Sort tasks by creation date.

    Args:
        tasks: List of task dictionaries
        descending: True for newest first, False for oldest first

    Returns:
        Sorted list of task dictionaries
    """
    if descending:
        return sorted(tasks, key=lambda x: datetime.fromisoformat(x.get('created_at', '')), reverse=True)
    else:
        return sorted(tasks, key=lambda x: datetime.fromisoformat(x.get('created_at', '')))


def apply_completion_sort(tasks: List[Dict[str, Any]], descending: bool = False) -> List[Dict[str, Any]]:
    """
    Sort tasks by completion status.

    Args:
        tasks: List of task dictionaries
        descending: True for completed first, False for pending first

    Returns:
        Sorted list of task dictionaries
    """
    if descending:
        # Completed first
        return sorted(tasks, key=lambda x: x.get('completed', False), reverse=True)
    else:
        # Pending first
        return sorted(tasks, key=lambda x: x.get('completed', False))


def apply_multiple_sort_criteria(tasks: List[Dict[str, Any]], sort_criteria: List[tuple]) -> List[Dict[str, Any]]:
    """
    Apply multiple sort criteria in order of precedence.

    Args:
        tasks: List of task dictionaries
        sort_criteria: List of tuples (field, is_descending)

    Returns:
        Sorted list of task dictionaries
    """
    # Sort by criteria in reverse order to achieve the correct precedence
    # (last sort is stable and determines final order)
    for field, is_descending in reversed(sort_criteria):
        if field == 'priority':
            tasks = apply_custom_priority_sort(tasks, is_descending)
        elif field == 'title':
            tasks = apply_alphabetical_sort(tasks, is_descending)
        elif field == 'created_at':
            tasks = apply_date_sort(tasks, is_descending)
        elif field == 'completed':
            tasks = apply_completion_sort(tasks, is_descending)

    return tasks


def validate_sort_parameters(sort_by: Optional[str], sort_order: Optional[str]) -> tuple[bool, Optional[str]]:
    """
    Validate sort parameters.

    Args:
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if sort_by and sort_by not in ["created_at", "priority", "title", "completed", "due_date"]:
        return False, f"sort_by must be one of: created_at, priority, title, completed, due_date"

    if sort_order and sort_order not in ["asc", "desc"]:
        return False, f"sort_order must be one of: asc, desc"

    return True, None


def optimize_sort_performance(tasks: List[Dict[str, Any]], sort_field: str) -> List[Dict[str, Any]]:
    """
    Apply performance optimizations for sorting operations.

    Args:
        tasks: List of task dictionaries
        sort_field: Field to sort by

    Returns:
        Potentially optimized list for sorting
    """
    # For large lists, we might apply different algorithms or optimizations
    # For now, just return the tasks as is
    return tasks