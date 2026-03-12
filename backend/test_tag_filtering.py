#!/usr/bin/env python3
"""
Test script to verify the tag filtering functionality
"""
import sys
import os
import asyncio
import json

# Add the backend/src directory to the Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from src.mcp.tools import list_tasks, add_task


async def test_tag_filtering():
    print("=== Testing Tag Filtering Functionality ===")

    # Use a test user ID
    test_user_id = "test_user_for_filtering"

    print("\n1. Adding test tasks with various tags...")

    # Add tasks with different tags
    await add_task(user_id=test_user_id, title="Work task 1", tags=["work", "urgent"])
    await add_task(user_id=test_user_id, title="Personal task 1", tags=["personal", "home"])
    await add_task(user_id=test_user_id, title="Work task 2", tags=["work", "meeting"])
    await add_task(user_id=test_user_id, title="Important task", tags=["important", "work"])
    await add_task(user_id=test_user_id, title="General task", tags=[])

    print("Tasks added successfully")

    print("\n2. Testing list_tasks with no filters (all tasks)...")
    all_tasks = await list_tasks(user_id=test_user_id)
    print(f"Total tasks: {all_tasks['total_count']}")
    for task in all_tasks['tasks']:
        print(f"  - {task['title']}: {task['tags']}")

    print("\n3. Testing list_tasks with 'work' tag filter...")
    work_tasks = await list_tasks(user_id=test_user_id, tags=["work"])
    print(f"Tasks with 'work' tag: {work_tasks['total_count']}")
    for task in work_tasks['tasks']:
        print(f"  - {task['title']}: {task['tags']}")

    print("\n4. Testing list_tasks with 'personal' tag filter...")
    personal_tasks = await list_tasks(user_id=test_user_id, tags=["personal"])
    print(f"Tasks with 'personal' tag: {personal_tasks['total_count']}")
    for task in personal_tasks['tasks']:
        print(f"  - {task['title']}: {task['tags']}")

    print("\n5. Testing list_tasks with 'important' tag filter...")
    important_tasks = await list_tasks(user_id=test_user_id, tags=["important"])
    print(f"Tasks with 'important' tag: {important_tasks['total_count']}")
    for task in important_tasks['tasks']:
        print(f"  - {task['title']}: {task['tags']}")

    print("\n6. Testing list_tasks with non-existent tag filter...")
    fake_tasks = await list_tasks(user_id=test_user_id, tags=["fake"])
    print(f"Tasks with 'fake' tag: {fake_tasks['total_count']}")
    for task in fake_tasks['tasks']:
        print(f"  - {task['title']}: {task['tags']}")

    print("\n=== Tag Filtering Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_tag_filtering())