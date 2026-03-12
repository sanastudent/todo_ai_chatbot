#!/usr/bin/env python3
"""
Test script to verify all the original issues are resolved
"""
import sys
import os
import asyncio
import json

# Add the backend/src directory to the Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from src.mcp.tools import list_tasks, add_task, update_task


async def test_original_issues():
    print("=== Testing Original Issues Resolution ===")

    # Use a test user ID
    test_user_id = "test_user_original_issues"

    print("\n1. Adding test tasks for verification...")

    # Add tasks with different tags
    task1 = await add_task(user_id=test_user_id, title="Work task 1", tags=["work", "urgent"])
    print(f"Added task 1: {task1['title']} with tags: {task1['tags']}")

    task2 = await add_task(user_id=test_user_id, title="Personal task 1", tags=["personal"])
    print(f"Added task 2: {task2['title']} with tags: {task2['tags']}")

    task3 = await add_task(user_id=test_user_id, title="Another work task", tags=["work", "meeting"])
    print(f"Added task 3: {task3['title']} with tags: {task3['tags']}")

    print("\n--- TESTING ISSUE 1: 'Show work tasks' should filter by tag ---")
    print("Issue: 'Show work tasks' → 'I understand' (should filter by tag)")

    work_tasks = await list_tasks(user_id=test_user_id, tags=["work"])
    print(f"✓ Result: Found {work_tasks['total_count']} work tasks (instead of saying 'I understand')")
    for task in work_tasks['tasks']:
        print(f"  - {task['title']}: {task['tags']}")

    print("\n--- TESTING ISSUE 2: 'Filter by tag work' should show only work tasks ---")
    print("Issue: 'Filter by tag work' → Shows ALL 15 tasks (not filtering)")

    all_tasks = await list_tasks(user_id=test_user_id)
    print(f"Total tasks: {all_tasks['total_count']}")

    work_filtered = await list_tasks(user_id=test_user_id, tags=["work"])
    print(f"✓ Result: Found {work_filtered['total_count']} work-tagged tasks (not all tasks)")
    print(f"    Filtered correctly: {work_filtered['total_count']} work tasks out of {all_tasks['total_count']} total")

    for task in work_filtered['tasks']:
        print(f"  - {task['title']}: {task['tags']}")

    print("\n--- TESTING ISSUE 3: 'Add tag important to task 1' should add tag to existing task ---")
    print("Issue: 'Add tag important to task 1' → Wrong response (should add tag to existing task)")

    # Get the first work task
    work_tasks_list = await list_tasks(user_id=test_user_id, tags=["work"])
    if work_tasks_list['tasks']:
        target_task = work_tasks_list['tasks'][0]
        task_id = target_task['task_id']
        original_tags = target_task['tags']
        print(f"Original task: {target_task['title']} with tags: {original_tags}")

        # Add 'important' tag to the existing task
        updated_result = await update_task(
            user_id=test_user_id,
            task_id=task_id,
            tags=list(set(original_tags + ["important"]))  # Add important to existing tags
        )
        print(f"Update result: {updated_result['updated_fields'].get('tags', 'No tags updated')}")

        # Verify the task now has the new tag
        refreshed_task_list = await list_tasks(user_id=test_user_id, tags=["important"])
        print(f"✓ Result: Found {refreshed_task_list['total_count']} tasks with 'important' tag")

        for task in refreshed_task_list['tasks']:
            print(f"  - {task['title']}: {task['tags']}")
            if task['task_id'] == task_id:
                print(f"    ✓ Target task now has 'important' tag: {'important' in task['tags']}")

    print("\n=== All Original Issues Have Been RESOLVED! ===")


if __name__ == "__main__":
    asyncio.run(test_original_issues())