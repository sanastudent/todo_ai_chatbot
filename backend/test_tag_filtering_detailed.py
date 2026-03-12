#!/usr/bin/env python3
"""
Detailed test script to verify the tag filtering functionality
"""
import sys
import os
import asyncio
import json

# Add the backend/src directory to the Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from src.mcp.tools import list_tasks, add_task


async def test_tag_filtering_detailed():
    print("=== Detailed Tag Filtering Test ===")

    # Use a test user ID
    test_user_id = "test_user_detailed_filtering"

    print("\n1. Checking existing tasks with tags...")
    all_tasks = await list_tasks(user_id=test_user_id)
    print(f"Total tasks for user: {all_tasks['total_count']}")

    for task in all_tasks['tasks']:
        print(f"  - {task['title']}: {task['tags']}")

    print("\n2. Adding some test tasks with specific tags...")
    # Add a few more test tasks to have consistent data
    await add_task(user_id=test_user_id, title="Test work task 1", tags=["work", "urgent"])
    await add_task(user_id=test_user_id, title="Test personal task 1", tags=["personal", "home"])
    await add_task(user_id=test_user_id, title="Test work task 2", tags=["work", "meeting"])
    await add_task(user_id=test_user_id, title="Test general task", tags=[])

    # Refresh the list
    all_tasks_after = await list_tasks(user_id=test_user_id)
    print(f"Total tasks after adding: {all_tasks_after['total_count']}")

    print("\n3. Testing 'Show work tasks' filtering...")
    work_tasks = await list_tasks(user_id=test_user_id, tags=["work"])
    print(f"Work tasks found: {work_tasks['total_count']}")
    for task in work_tasks['tasks']:
        print(f"  - {task['title']}: {task['tags']}")

    print("\n4. Testing 'Show personal tasks' filtering...")
    personal_tasks = await list_tasks(user_id=test_user_id, tags=["personal"])
    print(f"Personal tasks found: {personal_tasks['total_count']}")
    for task in personal_tasks['tasks']:
        print(f"  - {task['title']}: {task['tags']}")

    print("\n5. Testing 'Show urgent tasks' filtering...")
    urgent_tasks = await list_tasks(user_id=test_user_id, tags=["urgent"])
    print(f"Urgent tasks found: {urgent_tasks['total_count']}")
    for task in urgent_tasks['tasks']:
        print(f"  - {task['title']}: {task['tags']}")

    print("\n6. Testing multiple tag filtering (work AND urgent)...")
    work_urgent_tasks = await list_tasks(user_id=test_user_id, tags=["work", "urgent"])
    print(f"Work AND urgent tasks found: {work_urgent_tasks['total_count']}")
    for task in work_urgent_tasks['tasks']:
        print(f"  - {task['title']}: {task['tags']}")

    print("\n7. Testing non-existent tag filtering...")
    fake_tasks = await list_tasks(user_id=test_user_id, tags=["nonexistent"])
    print(f"Non-existent tag tasks found: {fake_tasks['total_count']}")

    print("\n=== Detailed Tag Filtering Test Complete ===")
    print("If work tasks were found, then the filtering is working correctly!")


if __name__ == "__main__":
    asyncio.run(test_tag_filtering_detailed())