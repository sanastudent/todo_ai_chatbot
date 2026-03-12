#!/usr/bin/env python3
"""
Test script to verify that tags functionality works correctly.
This script will:
1. Add tasks with tags
2. List tasks with tag filtering
3. Verify that filtering works as expected
"""

import sys
import os
import asyncio
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.mcp.tools import add_task, list_tasks


async def test_tags_functionality():
    print("=== Testing Tags Functionality ===")

    # Use a test user ID
    test_user_id = "test_user_123"

    # Clean up any existing test tasks
    print("\n1. Listing all tasks for test user before adding new ones...")
    all_tasks_before = await list_tasks(user_id=test_user_id)
    print(f"Found {len(all_tasks_before['tasks'])} existing tasks")

    # Add tasks with different tags
    print("\n2. Adding tasks with different tags...")

    task1 = await add_task(
        user_id=test_user_id,
        title="Work task 1",
        description="First work-related task",
        tags=["work", "urgent"]
    )
    print(f"Added task 1: {task1}")

    task2 = await add_task(
        user_id=test_user_id,
        title="Personal task 1",
        description="First personal task",
        tags=["personal", "home"]
    )
    print(f"Added task 2: {task2}")

    task3 = await add_task(
        user_id=test_user_id,
        title="Work task 2",
        description="Second work-related task",
        tags=["work", "meeting"]
    )
    print(f"Added task 3: {task3}")

    task4 = await add_task(
        user_id=test_user_id,
        title="Important task",
        description="High priority task",
        priority="high",
        tags=["important", "work"]
    )
    print(f"Added task 4: {task4}")

    # List all tasks
    print("\n3. Listing all tasks for test user...")
    all_tasks = await list_tasks(user_id=test_user_id)
    print(f"Found {len(all_tasks['tasks'])} total tasks:")
    for task in all_tasks['tasks']:
        print(f"  - {task['title']} (tags: {task['tags']}, priority: {task['priority']})")

    # Test filtering by tags
    print("\n4. Testing tag filtering...")

    # Filter by 'work' tag
    work_tasks = await list_tasks(user_id=test_user_id, tags=["work"])
    print(f"Tasks with 'work' tag ({len(work_tasks['tasks'])}):")
    for task in work_tasks['tasks']:
        print(f"  - {task['title']} (tags: {task['tags']})")

    # Filter by 'personal' tag
    personal_tasks = await list_tasks(user_id=test_user_id, tags=["personal"])
    print(f"\nTasks with 'personal' tag ({len(personal_tasks['tasks'])}):")
    for task in personal_tasks['tasks']:
        print(f"  - {task['title']} (tags: {task['tags']})")

    # Filter by 'important' tag
    important_tasks = await list_tasks(user_id=test_user_id, tags=["important"])
    print(f"\nTasks with 'important' tag ({len(important_tasks['tasks'])}):")
    for task in important_tasks['tasks']:
        print(f"  - {task['title']} (tags: {task['tags']}, priority: {task['priority']})")

    # Test filtering with multiple tags
    work_and_urgent_tasks = await list_tasks(user_id=test_user_id, tags=["work", "urgent"])
    print(f"\nTasks with 'work' AND 'urgent' tags ({len(work_and_urgent_tasks['tasks'])}):")
    for task in work_and_urgent_tasks['tasks']:
        print(f"  - {task['title']} (tags: {task['tags']})")

    # Test combination of filters (tags + priority)
    high_priority_work_tasks = await list_tasks(user_id=test_user_id, tags=["work"], priority=["high"])
    print(f"\nHigh priority work tasks ({len(high_priority_work_tasks['tasks'])}):")
    for task in high_priority_work_tasks['tasks']:
        print(f"  - {task['title']} (tags: {task['tags']}, priority: {task['priority']})")

    print("\n=== Tags Functionality Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_tags_functionality())