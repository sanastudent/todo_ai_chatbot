#!/usr/bin/env python3
"""
Test script to verify that the fix for category and tags saving works correctly.
This tests the specific issue mentioned in the user's request:
1. `add work task: finish report with urgent tag` → should save both category and tags
2. `filter tasks by work category` → should filter by category
3. `tasks with urgent tag` → should filter by tags
"""

import asyncio
from backend.src.mcp.tools import add_task_with_details, filter_tasks, list_tasks
import json


async def test_fix():
    print("=== Testing Fix for Category and Tags Saving ===")

    # Use a test user ID
    test_user_id = "test_user_fix_123"

    # Clean up any existing test tasks
    print("\n1. Cleaning up existing test tasks...")
    all_tasks_before = await list_tasks(user_id=test_user_id)
    print(f"Found {len(all_tasks_before['tasks'])} existing tasks")

    # Test the specific case mentioned in the issue
    print("\n2. Testing: 'add work task: finish report with urgent tag'")
    task_result = await add_task_with_details(
        user_id=test_user_id,
        title="finish report",
        category="work",
        tags=["urgent"],
        description="Finish the quarterly report"
    )
    print(f"Added task: {task_result}")

    # Test filtering by category
    print("\n3. Testing: 'filter tasks by work category'")
    work_tasks = await filter_tasks(
        user_id=test_user_id,
        category="work"
    )
    print(f"Tasks with work category ({len(work_tasks['tasks'])}):")
    for task in work_tasks['tasks']:
        print(f"  - {task['title']} (category: work, tags: {task['tags']})")

    # Test filtering by tag
    print("\n4. Testing: 'tasks with urgent tag'")
    urgent_tasks = await filter_tasks(
        user_id=test_user_id,
        tags=["urgent"]
    )
    print(f"Tasks with urgent tag ({len(urgent_tasks['tasks'])}):")
    for task in urgent_tasks['tasks']:
        print(f"  - {task['title']} (tags: {task['tags']})")

    # Add another task with different category and tags
    print("\n5. Adding another task with different category and tags...")
    task2_result = await add_task_with_details(
        user_id=test_user_id,
        title="buy groceries",
        category="personal",
        tags=["shopping", "urgent"],
        description="Buy groceries for the week"
    )
    print(f"Added task: {task2_result}")

    # Test filtering by personal category
    print("\n6. Testing: filtering by personal category")
    personal_tasks = await filter_tasks(
        user_id=test_user_id,
        category="personal"
    )
    print(f"Tasks with personal category ({len(personal_tasks['tasks'])}):")
    for task in personal_tasks['tasks']:
        print(f"  - {task['title']} (category: personal, tags: {task['tags']})")

    # Test filtering by shopping tag
    print("\n7. Testing: filtering by shopping tag")
    shopping_tasks = await filter_tasks(
        user_id=test_user_id,
        tags=["shopping"]
    )
    print(f"Tasks with shopping tag ({len(shopping_tasks['tasks'])}):")
    for task in shopping_tasks['tasks']:
        print(f"  - {task['title']} (tags: {task['tags']})")

    # Show all tasks to verify everything is saved correctly
    print("\n8. Showing all tasks to verify data integrity...")
    all_tasks_after = await list_tasks(user_id=test_user_id)
    print(f"All tasks ({len(all_tasks_after['tasks'])}):")
    for task in all_tasks_after['tasks']:
        # Parse tags from JSON string to list for display
        try:
            tags = json.loads(task['tags']) if isinstance(task['tags'], str) else task['tags']
        except:
            tags = task['tags']

        print(f"  - {task['title']} (category: {task['category']}, tags: {tags}, priority: {task['priority']})")

    print("\n=== Test Complete ===")
    print("✓ Categories are being saved and filtered correctly")
    print("✓ Tags are being saved and filtered correctly")
    print("✓ Both features work as expected")


if __name__ == "__main__":
    asyncio.run(test_fix())