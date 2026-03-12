from typing import Dict, Any, Optional, List
from uuid import uuid4
from datetime import datetime
import json
import traceback
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import logging

from src.models.task import Task
from src.services.database import async_engine
from src.utils.validation import validate_and_sanitize_priority, validate_and_sanitize_tags


logger = logging.getLogger(__name__)


async def add_task(user_id: str, title: str, description: Optional[str] = None, priority: Optional[str] = None, tags: Optional[List[str]] = None, db_session=None) -> Dict[str, Any]:
    """
    Create a new task for the user.

    Args:
        user_id: User identifier (must match authenticated user)
        title: Short description of the task (what needs to be done)
        description: Optional additional details or notes about the task
        priority: Optional priority level of the task (high, medium, low)
        tags: Optional list of tags to associate with the task
        db_session: Optional database session to use (if not provided, creates a new one)

    Returns:
        Dict containing task_id, title, and created_at

    Raises:
        ValueError: If validation fails
        Exception: If database operation fails
    """
    # Input validation
    if not user_id or not user_id.strip():
        raise ValueError("Invalid user_id")

    if not title or not title.strip():
        raise ValueError("Title cannot be empty")

    if len(title.strip()) > 200:
        raise ValueError("Title cannot exceed 200 characters")

    if description and len(description) > 2000:
        raise ValueError("Description cannot exceed 2000 characters")

    # Validate priority if provided
    priority_is_valid, sanitized_priority, priority_error = validate_and_sanitize_priority(priority)
    if not priority_is_valid:
        raise ValueError(priority_error)

    # Validate tags if provided
    tags_are_valid, sanitized_tags, tags_error = validate_and_sanitize_tags(tags)
    if not tags_are_valid:
        raise ValueError(tags_error)

    # Ensure we have a valid session
    session_provided = db_session is not None
    session = db_session

    try:
        if not session_provided:
            session = AsyncSession(async_engine)
            await session.__aenter__()  # Enter context manager manually

        # Check if task with same user_id and title already exists
        existing_task_query = select(Task).where(
            Task.user_id == user_id,
            Task.title == title.strip()
        )
        existing_task_result = await session.exec(existing_task_query)
        existing_task = existing_task_result.first()

        if existing_task:
            # Task already exists, return existing task info
            return {
                "task_id": existing_task.id,
                "title": existing_task.title,
                "created_at": existing_task.created_at.isoformat(),
                "was_duplicate": True  # Indicates this was a duplicate
            }

        # Create task instance if it doesn't exist
        task = Task(
            id=str(uuid4()),
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            completed=False,
            priority=sanitized_priority,
            category="general",  # Default category for basic tasks
            tags=json.dumps(sanitized_tags, ensure_ascii=False),  # Store tags as JSON string with Unicode support
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Insert into database
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "task_id": task.id,
            "title": task.title,
            "created_at": task.created_at.isoformat(),
            "priority": task.priority,
            "tags": task.tags,
            "was_duplicate": False  # Indicates this was newly created
        }
    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        logger.error(f"Failed to create task for user {user_id}: {str(e)}")
        raise Exception("Failed to create task")
    finally:
        # Only close the session if we created it
        if not session_provided and session:
            await session.close()


async def list_tasks(user_id: str, completed: Optional[bool] = None, priority: Optional[List[str]] = None, tags: Optional[List[str]] = None, search_term: Optional[str] = None, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None, sort_by: Optional[str] = None, sort_order: Optional[str] = None, limit: Optional[int] = 50, offset: Optional[int] = 0, db_session=None) -> Dict[str, Any]:
    """
    Retrieve all tasks for the user, with optional filtering, searching, and sorting capabilities.

    Args:
        user_id: User identifier (must match authenticated user)
        completed: Optional filter: true=only completed tasks, false=only pending tasks, omit=all tasks
        priority: Optional list of priority levels to filter by (high, medium, low)
        tags: Optional list of tags to filter by
        search_term: Optional keyword to search in task title, description, or tags
        date_from: Optional filter for tasks created after this date
        date_to: Optional filter for tasks created before this date
        sort_by: Optional field to sort by (created_at, priority, title, completed, due_date)
        sort_order: Optional sort order (asc, desc)
        limit: Maximum number of tasks to return (default 50, max 100)
        offset: Number of tasks to skip for pagination (default 0)
        db_session: Optional database session to use (if not provided, creates a new one)

    Returns:
        Dict containing a list of tasks and metadata

    Raises:
        ValueError: If validation fails
        Exception: If database operation fails
    """
    print(f"DEBUG: list_tasks called with filters: user_id={user_id}, completed={completed}, priority={priority}, tags={tags}, search_term={search_term}")
    # User validation
    if not user_id or not user_id.strip():
        raise ValueError("Invalid user_id")

    # Validate and sanitize parameters
    if limit and (limit < 1 or limit > 100):
        raise ValueError("Limit must be between 1 and 100")

    if offset and offset < 0:
        raise ValueError("Offset must be greater than or equal to 0")

    # Validate priority if provided
    if priority:
        for p in priority:
            is_valid, _, error = validate_and_sanitize_priority(p)
            if not is_valid:
                raise ValueError(error)

    # Validate tags if provided
    if tags:
        is_valid, _, error = validate_and_sanitize_tags(tags)
        if not is_valid:
            raise ValueError(error)

    # Validate sort parameters
    from src.services.sort import validate_sort_parameters
    is_valid, error_msg = validate_sort_parameters(sort_by, sort_order)
    if not is_valid:
        raise ValueError(error_msg)

    # Validate combined filters
    from src.services.filter import validate_combined_filters
    filters_for_validation = {}
    if completed is not None:
        filters_for_validation['completed'] = completed
    if priority:
        filters_for_validation['priority'] = priority
    if tags:
        filters_for_validation['tags'] = tags
    if date_from:
        filters_for_validation['date_from'] = date_from
    if date_to:
        filters_for_validation['date_to'] = date_to

    is_valid, error_msg = validate_combined_filters(filters_for_validation)
    if not is_valid:
        raise ValueError(error_msg)

    # Ensure we have a valid session
    session_provided = db_session is not None
    session = db_session

    try:
        if not session_provided:
            session = AsyncSession(async_engine)
            await session.__aenter__()  # Enter context manager manually

        # Build query based on filters
        query = select(Task).where(Task.user_id == user_id)

        # Prepare filter dictionary for the filter service
        filters = {}
        if completed is not None:
            filters['completed'] = completed
        if priority:
            filters['priority'] = priority
        if tags:
            filters['tags'] = tags
        if date_from:
            filters['date_from'] = date_from
        if date_to:
            filters['date_to'] = date_to

        # Apply filters using the filter service
        from src.services.filter import apply_multi_criteria_filter
        query = apply_multi_criteria_filter(query, filters)

        # Apply search filter (search across title, description, and tags)
        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.where(
                (Task.title.ilike(search_pattern)) |
                (Task.description.ilike(search_pattern)) |
                (Task.tags.like(f'%"{search_term}"%'))  # Search for tags containing the term
            )

        # Apply sorting using database-level sorting where possible
        from sqlalchemy import case
        if sort_by == "priority":
            # Custom sorting for priority: high > medium > low
            priority_case = case(
                (Task.priority == 'high', 1),
                (Task.priority == 'medium', 2),
                (Task.priority == 'low', 3)
            )
            if sort_order == "desc":
                # For descending, we want high priority first, so ascending by priority case value
                query = query.order_by(priority_case.asc(), Task.created_at.desc())
            else:
                # For ascending, we want low priority first, so descending by priority case value
                query = query.order_by(priority_case.desc(), Task.created_at.desc())
        elif sort_by == "title":
            if sort_order == "desc":
                query = query.order_by(Task.title.desc(), Task.created_at.desc())
            else:
                query = query.order_by(Task.title.asc(), Task.created_at.desc())
        elif sort_by == "completed":
            if sort_order == "desc":
                query = query.order_by(Task.completed.desc(), Task.created_at.desc())
            else:
                query = query.order_by(Task.completed.asc(), Task.created_at.desc())
        elif sort_by == "due_date":
            if sort_order == "desc":
                query = query.order_by(Task.due_date.desc(), Task.created_at.desc())
            else:
                query = query.order_by(Task.due_date.asc(), Task.created_at.desc())
        elif sort_by == "created_at":
            if sort_order == "desc":
                query = query.order_by(Task.created_at.desc())
            else:
                query = query.order_by(Task.created_at.asc())
        else:
            # Default sort by created_at DESC
            query = query.order_by(Task.created_at.desc())

        # Apply limit and offset for pagination
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        # Use the session to execute the query
        results = await session.exec(query)
        tasks = results.all()

        # Count total matching tasks for pagination metadata
        count_query = select(Task).where(Task.user_id == user_id)

        # Apply same filters for counting
        count_query = apply_multi_criteria_filter(count_query, filters)

        if search_term:
            search_pattern = f"%{search_term}%"
            count_query = count_query.where(
                (Task.title.ilike(search_pattern)) |
                (Task.description.ilike(search_pattern)) |
                (Task.tags.like(f'%"{search_term}"%'))
            )

        count_results = await session.exec(count_query)
        total_count = len(count_results.all())

        # Format tasks for output
        formatted_tasks = []
        for task in tasks:
            # Parse tags from JSON string to list
            try:
                tags_list = json.loads(task.tags)
            except (ValueError, TypeError):
                tags_list = []

            task_dict = {
                "task_id": task.id,
                "title": task.title,
                "completed": task.completed,
                "priority": task.priority,
                "tags": tags_list,
                "created_at": task.created_at.isoformat()
            }
            # Include description if it exists
            if task.description:
                task_dict["description"] = task.description
            # Include updated_at if it exists
            if task.updated_at:
                task_dict["updated_at"] = task.updated_at.isoformat()

            formatted_tasks.append(task_dict)

        # If searching, rank the results by relevance (this overrides other sorts)
        if search_term:
            from src.services.search import rank_search_results
            formatted_tasks = rank_search_results(formatted_tasks, search_term)
        # Otherwise, apply sorting if specified
        elif sort_by and sort_by != "created_at":  # Only apply custom sorting if not default
            if sort_by == "priority":
                from src.services.sort import apply_custom_priority_sort
                descending = sort_order != "asc"  # Default to descending for priority
                formatted_tasks = apply_custom_priority_sort(formatted_tasks, descending)
            elif sort_by == "title":
                from src.services.sort import apply_alphabetical_sort
                descending = sort_order == "desc"
                formatted_tasks = apply_alphabetical_sort(formatted_tasks, descending)
            elif sort_by == "completed":
                from src.services.sort import apply_completion_sort
                descending = sort_order == "desc"
                formatted_tasks = apply_completion_sort(formatted_tasks, descending)

        # Prepare filtered_by metadata
        filtered_by = {}
        if completed is not None:
            filtered_by["completed"] = completed
        if priority:
            filtered_by["priority"] = priority
        if tags:
            filtered_by["tags"] = tags
        if search_term:
            filtered_by["search_term"] = search_term

        return {
            "tasks": formatted_tasks,
            "total_count": total_count,
            "filtered_by": filtered_by
        }
    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve tasks for user {user_id}: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise
    finally:
        # Only close the session if we created it
        if not session_provided and session:
            await session.close()


async def complete_task(user_id: str, task_id: str, db_session=None) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        user_id: User identifier (must match authenticated user)
        task_id: Unique identifier of the task to complete
        db_session: Optional database session to use (if not provided, creates a new one)

    Returns:
        Dict containing task_id, completed status, and updated_at timestamp

    Raises:
        ValueError: If validation fails
        Exception: If database operation fails
    """
    # User and task validation
    if not user_id or not user_id.strip():
        raise ValueError("Invalid user_id")

    if not task_id or not task_id.strip():
        raise ValueError("Invalid task_id")

    # Ensure we have a valid session
    session_provided = db_session is not None
    session = db_session

    try:
        if not session_provided:
            session = AsyncSession(async_engine)
            await session.__aenter__()  # Enter context manager manually

        # Get the task
        task = await session.get(Task, task_id)

        # Check if task exists and belongs to the user
        if not task:
            raise ValueError("Task not found or does not belong to user")

        if task.user_id != user_id:
            raise ValueError("Task does not belong to user")

        # Check if already completed (idempotency)
        if task.completed:
            return {
                "task_id": task.id,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            }

        # Update task to completed
        task.completed = True
        task.updated_at = datetime.utcnow()

        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "task_id": task.id,
            "completed": task.completed,
            "updated_at": task.updated_at.isoformat()
        }
    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        logger.error(f"Failed to complete task {task_id} for user {user_id}: {str(e)}")
        raise Exception("Failed to complete task")
    finally:
        # Only close the session if we created it
        if not session_provided and session:
            await session.close()


async def update_task(user_id: str, task_id: str, title: Optional[str] = None, description: Optional[str] = None, priority: Optional[str] = None, tags: Optional[List[str]] = None, db_session=None) -> Dict[str, Any]:
    """
    Update the title, description, priority, or tags of an existing task.

    Args:
        user_id: User identifier (must match authenticated user)
        task_id: Unique identifier of the task to update
        title: New task title (optional - only if changing title)
        description: New task description (optional - only if changing description, null to clear)
        priority: New priority level for the task (optional - only if changing priority)
        tags: New list of tags for the task (optional - only if changing tags)
        db_session: Optional database session to use (if not provided, creates a new one)

    Returns:
        Dict containing task_id, updated_fields, and updated_at timestamp

    Raises:
        ValueError: If validation fails
        Exception: If database operation fails
    """
    # User and task validation
    if not user_id or not user_id.strip():
        raise ValueError("Invalid user_id")

    if not task_id or not task_id.strip():
        raise ValueError("Invalid task_id")

    # At least one field must be provided
    if title is None and description is None and priority is None and tags is None:
        raise ValueError("At least one field (title, description, priority, or tags) must be provided")

    # Title validation if provided
    if title is not None:
        title = title.strip()
        if not title:
            raise ValueError("Title cannot be empty")
        if len(title) > 200:
            raise ValueError("Title cannot exceed 200 characters")

    # Description validation if provided
    if description is not None:
        if len(description) > 2000:
            raise ValueError("Description cannot exceed 2000 characters")

    # Priority validation if provided
    priority_is_valid = True
    sanitized_priority = None
    priority_error = None
    if priority is not None:
        priority_is_valid, sanitized_priority, priority_error = validate_and_sanitize_priority(priority)
        if not priority_is_valid:
            raise ValueError(priority_error)

    # Tags validation if provided
    tags_are_valid = True
    sanitized_tags = None
    tags_error = None
    if tags is not None:
        tags_are_valid, sanitized_tags, tags_error = validate_and_sanitize_tags(tags)
        if not tags_are_valid:
            raise ValueError(tags_error)

    # Ensure we have a valid session
    session_provided = db_session is not None
    session = db_session

    try:
        if not session_provided:
            session = AsyncSession(async_engine)
            await session.__aenter__()  # Enter context manager manually

        # Get the task
        task = await session.get(Task, task_id)

        # Check if task exists and belongs to the user
        if not task:
            raise ValueError("Task not found or does not belong to user")

        if task.user_id != user_id:
            raise ValueError("Task does not belong to user")

        # Update the fields that were provided
        updated_fields = {}

        if title is not None and task.title != title:
            task.title = title
            updated_fields["title"] = title

        if description is not None:
            task.description = description
            updated_fields["description"] = description

        if priority is not None and task.priority != sanitized_priority:
            task.priority = sanitized_priority
            updated_fields["priority"] = sanitized_priority

        if tags is not None:
            task.tags = json.dumps(sanitized_tags, ensure_ascii=False)  # Store tags as JSON string with Unicode support
            updated_fields["tags"] = sanitized_tags

        task.updated_at = datetime.utcnow()
        updated_fields["updated_at"] = task.updated_at.isoformat()

        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "task_id": task.id,
            "updated_fields": updated_fields,
            "updated_at": task.updated_at.isoformat()
        }
    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        logger.error(f"Failed to update task {task_id} for user {user_id}: {str(e)}")
        raise Exception("Failed to update task")
    finally:
        # Only close the session if we created it
        if not session_provided and session:
            await session.close()


async def delete_task(user_id: str, task_id: str, db_session=None) -> Dict[str, Any]:
    """
    Permanently delete a task.

    Args:
        user_id: User identifier (must match authenticated user)
        task_id: Unique identifier of the task to delete
        db_session: Optional database session to use (if not provided, creates a new one)

    Returns:
        Dict containing success status and task_id

    Raises:
        ValueError: If validation fails
        Exception: If database operation fails
    """
    # User and task validation
    if not user_id or not user_id.strip():
        raise ValueError("Invalid user_id")

    if not task_id or not task_id.strip():
        raise ValueError("Invalid task_id")

    # Ensure we have a valid session
    session_provided = db_session is not None
    session = db_session

    try:
        if not session_provided:
            session = AsyncSession(async_engine)
            await session.__aenter__()  # Enter context manager manually

        # Get the task
        task = await session.get(Task, task_id)

        # Check if task exists and belongs to the user
        if not task:
            raise ValueError("Task not found or does not belong to user")

        if task.user_id != user_id:
            raise ValueError("Task does not belong to user")

        # Delete the task from the database
        await session.delete(task)
        await session.commit()

        return {
            "success": True,
            "task_id": task.id
        }
    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        logger.error(f"Failed to delete task {task_id} for user {user_id}: {str(e)}")
        raise Exception("Failed to delete task")
    finally:
        # Only close the session if we created it
        if not session_provided and session:
            await session.close()


async def search_tasks(user_id: str, query: str, db_session=None) -> Dict[str, Any]:
    """
    Search for tasks by keyword across title, description, and tags.

    Args:
        user_id: User identifier (must match authenticated user)
        query: Search query string
        db_session: Optional database session to use (if not provided, creates a new one)

    Returns:
        Dict containing matching tasks and metadata

    Raises:
        ValueError: If validation fails
        Exception: If database operation fails
    """
    print(f"[DEBUG] search_tasks called with query: {query}")
    return await list_tasks(user_id=user_id, search_term=query, db_session=db_session)


async def filter_tasks(user_id: str, status: Optional[str] = None, priority: Optional[List[str]] = None, tags: Optional[List[str]] = None, category: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, db_session=None) -> Dict[str, Any]:
    """
    Filter tasks based on multiple criteria.

    Args:
        user_id: User identifier (must match authenticated user)
        status: Optional status filter ('pending', 'completed', 'all')
        priority: Optional list of priority levels to filter by (high, medium, low)
        tags: Optional list of tags to filter by
        category: Optional category filter (for future extension)
        date_from: Optional start date filter (ISO format: YYYY-MM-DD) - includes tasks with due_date >= date_from
        date_to: Optional end date filter (ISO format: YYYY-MM-DD) - includes tasks with due_date <= date_to
        db_session: Optional database session to use (if not provided, creates a new one)

    Returns:
        Dict containing filtered tasks and metadata

    Raises:
        ValueError: If validation fails
        Exception: If database operation fails
    """
    # User validation
    if not user_id or not user_id.strip():
        raise ValueError("Invalid user_id")

    # Normalize status parameter
    completed_filter = None
    if status and status.lower() in ['pending', 'incomplete', 'not_done']:
        completed_filter = False
    elif status and status.lower() in ['completed', 'done', 'finished']:
        completed_filter = True
    elif status and status.lower() in ['all', 'any']:
        completed_filter = None  # Don't filter by completion status

    # Validate priority if provided
    if priority:
        for p in priority:
            is_valid, _, error = validate_and_sanitize_priority(p)
            if not is_valid:
                raise ValueError(error)

    # Validate tags if provided
    if tags:
        is_valid, _, error = validate_and_sanitize_tags(tags)
        if not is_valid:
            raise ValueError(error)

    # Ensure we have a valid session
    session_provided = db_session is not None
    session = db_session

    try:
        if not session_provided:
            session = AsyncSession(async_engine)
            await session.__aenter__()  # Enter context manager manually

        # Build query based on filters
        query = select(Task).where(Task.user_id == user_id)

        # Apply completion status filter
        if completed_filter is not None:
            query = query.where(Task.completed == completed_filter)

        # Apply priority filter
        if priority:
            query = query.where(Task.priority.in_(priority))

        # Apply tags filter (match any of the specified tags)
        if tags:
            for tag in tags:
                query = query.where(Task.tags.like(f'%"{tag}"%'))

        # Apply category filter
        if category:
            query = query.where(Task.category == category)

        # Apply date filters
        if date_from:
            from datetime import datetime, date
            try:
                # Handle both date and datetime formats
                if len(date_from) <= 10:  # Just a date string like 'YYYY-MM-DD'
                    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                else:  # Full datetime string
                    date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00') if 'Z' in date_from else date_from)
                # Compare with the date part of the due_date field, handling NULLs
                query = query.where((Task.due_date.is_not(None)) & (Task.due_date >= date_from_obj))
            except ValueError:
                try:
                    # If the above fails, try as date object
                    date_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                    query = query.where((Task.due_date.is_not(None)) & (Task.due_date >= date_obj))
                except ValueError:
                    pass  # Invalid date format, skip the filter

        if date_to:
            from datetime import datetime, date
            try:
                # Handle both date and datetime formats
                if len(date_to) <= 10:  # Just a date string like 'YYYY-MM-DD'
                    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                else:  # Full datetime string
                    date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00') if 'Z' in date_to else date_to)
                # Compare with the date part of the due_date field, handling NULLs
                query = query.where((Task.due_date.is_not(None)) & (Task.due_date <= date_to_obj))
            except ValueError:
                try:
                    # If the above fails, try as date object
                    date_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                    query = query.where((Task.due_date.is_not(None)) & (Task.due_date <= date_obj))
                except ValueError:
                    pass  # Invalid date format, skip the filter

        # Apply default sorting
        query = query.order_by(Task.created_at.desc())

        # Execute query
        results = await session.exec(query)
        tasks = results.all()

        # Format tasks for output
        formatted_tasks = []
        for task in tasks:
            # Parse tags from JSON string to list
            try:
                tags_list = json.loads(task.tags)
            except (ValueError, TypeError):
                tags_list = []

            task_dict = {
                "task_id": task.id,
                "title": task.title,
                "completed": task.completed,
                "priority": task.priority,
                "tags": tags_list,
                "created_at": task.created_at.isoformat()
            }
            # Include description if it exists
            if task.description:
                task_dict["description"] = task.description
            # Include updated_at if it exists
            if task.updated_at:
                task_dict["updated_at"] = task.updated_at.isoformat()

            formatted_tasks.append(task_dict)

        # Prepare filter metadata
        filter_metadata = {}
        if status:
            filter_metadata["status"] = status
        if priority:
            filter_metadata["priority"] = priority
        if tags:
            filter_metadata["tags"] = tags
        if category:
            filter_metadata["category"] = category
        if date_from:
            filter_metadata["date_from"] = date_from
        if date_to:
            filter_metadata["date_to"] = date_to

        return {
            "tasks": formatted_tasks,
            "total_count": len(formatted_tasks),
            "filters_applied": filter_metadata
        }

    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        logger.error(f"Failed to filter tasks for user {user_id}: {str(e)}")
        raise Exception("Failed to filter tasks")
    finally:
        # Only close the session if we created it
        if not session_provided and session:
            await session.close()


async def add_task_with_details(user_id: str, title: str, description: Optional[str] = None, priority: Optional[str] = None, tags: Optional[List[str]] = None, category: Optional[str] = None, due_date: Optional[str] = None, db_session=None) -> Dict[str, Any]:
    """
    Create a new task with detailed information.

    Args:
        user_id: User identifier (must match authenticated user)
        title: Short description of the task (what needs to be done)
        description: Optional additional details or notes about the task
        priority: Optional priority level of the task (high, medium, low)
        tags: Optional list of tags to associate with the task
        category: Optional category for the task (stored as a tag)
        due_date: Optional due date for the task (stored as part of description or tags)
        db_session: Optional database session to use (if not provided, creates a new one)

    Returns:
        Dict containing task_id, title, and created_at

    Raises:
        ValueError: If validation fails
        Exception: If database operation fails
    """
    # Input validation
    if not user_id or not user_id.strip():
        raise ValueError("Invalid user_id")

    if not title or not title.strip():
        raise ValueError("Title cannot be empty")

    if len(title.strip()) > 200:
        raise ValueError("Title cannot exceed 200 characters")

    if description and len(description) > 2000:
        raise ValueError("Description cannot exceed 2000 characters")

    # Validate priority if provided
    priority_is_valid, sanitized_priority, priority_error = validate_and_sanitize_priority(priority)
    if not priority_is_valid and priority is not None:
        raise ValueError(priority_error)

    # Combine tags with category if provided
    combined_tags = []
    if tags:
        is_valid, sanitized_tags, tags_error = validate_and_sanitize_tags(tags)
        if not is_valid:
            raise ValueError(tags_error)
        combined_tags.extend(sanitized_tags)

    # Add category as a tag if provided
    if category and category.strip():
        category_clean = category.strip().lower()
        if category_clean not in combined_tags:
            combined_tags.append(category_clean)

    # Ensure we have a valid session
    session_provided = db_session is not None
    session = db_session

    try:
        if not session_provided:
            session = AsyncSession(async_engine)
            await session.__aenter__()  # Enter context manager manually

        # Check if task with same user_id and title already exists
        existing_task_query = select(Task).where(
            Task.user_id == user_id,
            Task.title == title.strip()
        )
        existing_task_result = await session.exec(existing_task_query)
        existing_task = existing_task_result.first()

        if existing_task:
            # Task already exists, return existing task info
            return {
                "task_id": existing_task.id,
                "title": existing_task.title,
                "created_at": existing_task.created_at.isoformat(),
                "was_duplicate": True  # Indicates this was a duplicate
            }

        # Create task instance if it doesn't exist
        task = Task(
            id=str(uuid4()),
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            completed=False,
            priority=sanitized_priority if sanitized_priority else "medium",
            category=category if category else "general",  # Use provided category or default to "general"
            tags=json.dumps(combined_tags, ensure_ascii=False),  # Store tags as JSON string with Unicode support
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Insert into database
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "tags": combined_tags,
            "due_date": due_date,
            "created_at": task.created_at.isoformat(),
            "was_duplicate": False  # Indicates this was newly created
        }
    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        logger.error(f"Failed to create task for user {user_id}: {str(e)}")
        raise Exception("Failed to create task")
    finally:
        # Only close the session if we created it
        if not session_provided and session:
            await session.close()


async def get_task_stats(user_id: str, timeframe: Optional[str] = None, db_session=None) -> Dict[str, Any]:
    """
    Get statistics about user's tasks.

    Args:
        user_id: User identifier (must match authenticated user)
        timeframe: Optional timeframe for stats ('today', 'week', 'month', 'year', 'all')
        db_session: Optional database session to use (if not provided, creates a new one)

    Returns:
        Dict containing task statistics

    Raises:
        ValueError: If validation fails
        Exception: If database operation fails
    """
    # User validation
    if not user_id or not user_id.strip():
        raise ValueError("Invalid user_id")

    # Ensure we have a valid session
    session_provided = db_session is not None
    session = db_session

    try:
        if not session_provided:
            session = AsyncSession(async_engine)
            await session.__aenter__()  # Enter context manager manually

        # Build base query for all user tasks
        base_query = select(Task).where(Task.user_id == user_id)

        # Apply timeframe filter if specified
        if timeframe:
            from datetime import datetime, timedelta
            now = datetime.utcnow()

            if timeframe.lower() == 'today':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                base_query = base_query.where(Task.created_at >= start_date)
            elif timeframe.lower() == 'week':
                # Start of week (Monday)
                days_since_monday = now.weekday()
                start_date = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
                base_query = base_query.where(Task.created_at >= start_date)
            elif timeframe.lower() == 'month':
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                base_query = base_query.where(Task.created_at >= start_date)
            elif timeframe.lower() == 'year':
                start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                base_query = base_query.where(Task.created_at >= start_date)

        # Get all tasks matching criteria
        all_results = await session.exec(base_query)
        all_tasks = all_results.all()

        # Calculate stats
        total_tasks = len(all_tasks)
        completed_tasks = sum(1 for task in all_tasks if task.completed)
        pending_tasks = total_tasks - completed_tasks

        # Priority distribution
        priority_counts = {"high": 0, "medium": 0, "low": 0}
        for task in all_tasks:
            if task.priority in priority_counts:
                priority_counts[task.priority] += 1

        # Calculate completion percentage
        completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # Get most common tags
        all_tags = []
        for task in all_tasks:
            try:
                task_tags = json.loads(task.tags) if task.tags else []
                all_tags.extend(task_tags)
            except (ValueError, TypeError):
                continue

        from collections import Counter
        tag_frequency = dict(Counter(all_tags)) if all_tags else {}

        return {
            "user_id": user_id,
            "timeframe": timeframe,
            "stats": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
                "completion_percentage": round(completion_percentage, 2),
                "priority_distribution": priority_counts,
                "most_common_tags": tag_frequency
            },
            "generated_at": datetime.utcnow().isoformat()
        }

    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        logger.error(f"Failed to get task stats for user {user_id}: {str(e)}")
        raise Exception("Failed to get task stats")
    finally:
        # Only close the session if we created it
        if not session_provided and session:
            await session.close()


async def search_tasks(user_id: str, query: str, search_in: Optional[List[str]] = None, db_session=None) -> Dict[str, Any]:
    """
    Search for tasks by keyword across specified fields.

    Args:
        user_id: User identifier (must match authenticated user)
        query: Search query string
        search_in: Optional list of fields to search in ('title', 'description', 'tags', 'all')
                 If None, defaults to ['title', 'description', 'tags']
        db_session: Optional database session to use (if not provided, creates a new one)

    Returns:
        Dict containing matching tasks and metadata

    Raises:
        ValueError: If validation fails
        Exception: If database operation fails
    """
    print(f"[DEBUG] search_tasks called with query: {query}, search_in: {search_in}")

    # User validation
    if not user_id or not user_id.strip():
        raise ValueError("Invalid user_id")

    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    # Default search fields if not specified
    if search_in is None:
        search_in = ['title', 'description', 'tags']
    elif not isinstance(search_in, list):
        search_in = [search_in] if isinstance(search_in, str) else []

    # Ensure all search fields are valid
    valid_fields = {'title', 'description', 'tags', 'all'}
    invalid_fields = [field for field in search_in if field not in valid_fields]
    if invalid_fields:
        raise ValueError(f"Invalid search fields: {invalid_fields}. Valid fields: {valid_fields}")

    # If 'all' is specified, search in all fields
    if 'all' in search_in:
        search_in = ['title', 'description', 'tags']

    # Ensure we have a valid session
    session_provided = db_session is not None
    session = db_session

    try:
        if not session_provided:
            session = AsyncSession(async_engine)
            await session.__aenter__()  # Enter context manager manually

        # Build query based on search fields
        query_obj = select(Task).where(Task.user_id == user_id)

        conditions = []
        search_term = f"%{query}%"

        if 'title' in search_in:
            conditions.append(Task.title.ilike(search_term))
        if 'description' in search_in:
            conditions.append(Task.description.ilike(search_term))
        if 'tags' in search_in:
            conditions.append(Task.tags.like(f'%"{query}"%'))  # Search for tags containing the term

        if conditions:
            from sqlalchemy import or_
            query_obj = query_obj.where(or_(*conditions))

        # Execute query
        results = await session.exec(query_obj)
        tasks = results.all()

        # Format tasks for output
        formatted_tasks = []
        for task in tasks:
            # Parse tags from JSON string to list
            try:
                tags_list = json.loads(task.tags)
            except (ValueError, TypeError):
                tags_list = []

            task_dict = {
                "task_id": task.id,
                "title": task.title,
                "completed": task.completed,
                "priority": task.priority,
                "tags": tags_list,
                "created_at": task.created_at.isoformat()
            }
            # Include description if it exists
            if task.description:
                task_dict["description"] = task.description
            # Include updated_at if it exists
            if task.updated_at:
                task_dict["updated_at"] = task.updated_at.isoformat()

            formatted_tasks.append(task_dict)

        return {
            "tasks": formatted_tasks,
            "total_count": len(formatted_tasks),
            "search_query": query,
            "search_fields": search_in
        }

    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        logger.error(f"Failed to search tasks for user {user_id}: {str(e)}")
        raise Exception("Failed to search tasks")
    finally:
        # Only close the session if we created it
        if not session_provided and session:
            await session.close()


async def add_tag_to_task(user_id: str, task_id: str, tag: str, db_session=None) -> Dict[str, Any]:
    """
    Add a tag to an existing task.

    Args:
        user_id: User identifier (must match authenticated user)
        task_id: Unique identifier of the task to add tag to
        tag: Tag to add to the task
        db_session: Optional database session to use (if not provided, creates a new one)

    Returns:
        Dict containing task_id, updated_tags, and updated_at timestamp

    Raises:
        ValueError: If validation fails
        Exception: If database operation fails
    """
    print(f"[DEBUG] add_tag_to_task called with task_id: {task_id}, tag: {tag}")

    # Validate inputs
    if not user_id or not user_id.strip():
        raise ValueError("Invalid user_id")

    if not task_id or not task_id.strip():
        raise ValueError("Invalid task_id")

    if not tag or not tag.strip():
        raise ValueError("Tag cannot be empty")

    # Ensure we have a valid session
    session_provided = db_session is not None
    session = db_session

    try:
        if not session_provided:
            session = AsyncSession(async_engine)
            await session.__aenter__()  # Enter context manager manually

        # Get the task
        task = await session.get(Task, task_id)

        # Check if task exists and belongs to the user
        if not task:
            raise ValueError("Task not found or does not belong to user")

        if task.user_id != user_id:
            raise ValueError("Task does not belong to user")

        # Get current tags and add the new tag
        try:
            current_tags = json.loads(task.tags) if task.tags else []
        except (ValueError, TypeError):
            current_tags = []

        # Add the new tag if it doesn't already exist
        if tag not in current_tags:
            current_tags.append(tag)

        # Update the task with new tags - ensure proper encoding
        task.tags = json.dumps(current_tags, ensure_ascii=False)  # Store tags as JSON string with Unicode support
        task.updated_at = datetime.utcnow()

        session.add(task)
        await session.commit()
        await session.refresh(task)

        # Parse tags from JSON string to list for return
        try:
            tags_list = json.loads(task.tags)
        except (ValueError, TypeError):
            tags_list = []

        return {
            "task_id": task.id,
            "updated_tags": tags_list,
            "updated_at": task.updated_at.isoformat()
        }
    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        logger.error(f"Failed to add tag to task {task_id} for user {user_id}: {str(e)}")
        raise Exception("Failed to add tag to task")
    finally:
        # Only close the session if we created it
        if not session_provided and session:
            await session.close()


async def bulk_operations(user_id: str, operation: str, task_ids: Optional[List[str]] = None,
                        filter_criteria: Optional[Dict[str, Any]] = None,
                        new_value: Optional[Any] = None, db_session=None) -> Dict[str, Any]:
    """
    Perform bulk operations on multiple tasks.

    Args:
        user_id: User identifier (must match authenticated user)
        operation: Operation to perform ('update_priority', 'update_status', 'add_tag', 'delete', 'complete')
        task_ids: Optional list of specific task IDs to operate on
                  If None, uses filter_criteria to select tasks
        filter_criteria: Optional dictionary of criteria to filter tasks by
                        e.g., {'status': 'pending', 'priority': ['high'], 'tags': ['work']}
        new_value: New value to set (required for update operations)
        db_session: Optional database session to use (if not provided, creates a new one)

    Returns:
        Dict containing operation results

    Raises:
        ValueError: If validation fails
        Exception: If database operation fails
    """
    # User validation
    if not user_id or not user_id.strip():
        raise ValueError("Invalid user_id")

    # Validate operation
    valid_operations = {'update_priority', 'update_status', 'add_tag', 'delete', 'complete', 'uncomplete'}
    if operation not in valid_operations:
        raise ValueError(f"Invalid operation: {operation}. Valid operations: {valid_operations}")

    # Validate inputs based on operation
    if operation.startswith('update_') and new_value is None:
        raise ValueError(f"new_value is required for {operation} operation")

    if operation == 'add_tag' and (new_value is None or not isinstance(new_value, str) or not new_value.strip()):
        raise ValueError("new_value must be a non-empty string for add_tag operation")

    # Ensure we have a valid session
    session_provided = db_session is not None
    session = db_session

    try:
        if not session_provided:
            session = AsyncSession(async_engine)
            await session.__aenter__()  # Enter context manager manually

        # Build query to select tasks
        query = select(Task).where(Task.user_id == user_id)

        # Apply filters based on task_ids or filter_criteria
        if task_ids:
            # Operate on specific task IDs
            query = query.where(Task.id.in_(task_ids))
        elif filter_criteria:
            # Apply filter criteria
            if 'status' in filter_criteria:
                status = filter_criteria['status']
                if status in ['pending', 'incomplete', 'not_done']:
                    query = query.where(Task.completed == False)
                elif status in ['completed', 'done', 'finished']:
                    query = query.where(Task.completed == True)

            if 'priority' in filter_criteria and filter_criteria['priority']:
                priorities = filter_criteria['priority']
                if isinstance(priorities, str):
                    priorities = [priorities]
                query = query.where(Task.priority.in_(priorities))

            if 'tags' in filter_criteria and filter_criteria['tags']:
                tags = filter_criteria['tags']
                if isinstance(tags, str):
                    tags = [tags]
                for tag in tags:
                    query = query.where(Task.tags.like(f'%"{tag}"%'))
        else:
            # If neither task_ids nor filter_criteria provided, operate on all user tasks
            pass

        # Execute query to get tasks to operate on
        results = await session.exec(query)
        tasks_to_operate = results.all()

        # Perform the operation
        affected_task_ids = []
        failed_task_ids = []

        for task in tasks_to_operate:
            try:
                if operation == 'update_priority':
                    # Validate the new priority value
                    is_valid, sanitized_priority, error = validate_and_sanitize_priority(new_value)
                    if not is_valid:
                        failed_task_ids.append(task.id)
                        continue
                    task.priority = sanitized_priority
                elif operation == 'update_status':
                    # Expecting 'completed' or 'pending' as new_value
                    if new_value in ['completed', 'done', 'finished', True]:
                        task.completed = True
                    elif new_value in ['pending', 'incomplete', 'not_done', False]:
                        task.completed = False
                    else:
                        failed_task_ids.append(task.id)
                        continue
                elif operation == 'add_tag':
                    # Add tag to existing tags
                    try:
                        current_tags = json.loads(task.tags) if task.tags else []
                    except (ValueError, TypeError):
                        current_tags = []

                    if new_value not in current_tags:
                        current_tags.append(new_value)
                        task.tags = json.dumps(current_tags, ensure_ascii=False)  # Store tags as JSON string with Unicode support
                elif operation == 'complete':
                    task.completed = True
                elif operation == 'uncomplete':
                    task.completed = False
                elif operation == 'delete':
                    await session.delete(task)
                    affected_task_ids.append(task.id)
                    continue  # Skip the commit below for deleted tasks

                # Update timestamp for modified tasks
                if operation != 'delete':
                    task.updated_at = datetime.utcnow()
                    session.add(task)

                affected_task_ids.append(task.id)

            except Exception as e:
                logger.error(f"Failed to perform {operation} on task {task.id}: {str(e)}")
                failed_task_ids.append(task.id)

        # Commit all changes
        await session.commit()

        return {
            "operation": operation,
            "affected_task_count": len(affected_task_ids),
            "failed_task_count": len(failed_task_ids),
            "affected_task_ids": affected_task_ids,
            "failed_task_ids": failed_task_ids,
            "completed_at": datetime.utcnow().isoformat()
        }

    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        logger.error(f"Failed to perform bulk operation {operation} for user {user_id}: {str(e)}")
        raise Exception("Failed to perform bulk operation")
    finally:
        # Only close the session if we created it
        if not session_provided and session:
            await session.close()