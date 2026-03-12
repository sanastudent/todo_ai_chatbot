#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'src')
from mcp.tools import add_task, list_tasks, update_task
import asyncio

async def test_basic_functionality():
    print('Testing basic functionality...')
    test_user = 'verification_test'

    # Clean up first
    result = await list_tasks(user_id=test_user)
    print(f'Started with {len(result["tasks"])} tasks')

    # Test 1: Add task with priority
    task1 = await add_task(user_id=test_user, title='Test task 1', priority='high')
    print(f'Added task with high priority: {task1.get("priority", "unknown")}')

    # Test 2: Add task with tags
    task2 = await add_task(user_id=test_user, title='Test task 2', tags=['work', 'urgent'])
    print(f'Added task with tags: {task2.get("tags", "unknown")}')

    # Test 3: Update task priority
    tasks = await list_tasks(user_id=test_user)
    if tasks['tasks']:
        task_id = tasks['tasks'][0]['task_id']
        result = await update_task(user_id=test_user, task_id=task_id, priority='low')
        print(f'Updated task priority: {result["updated_fields"].get("priority", "not changed")}')

    # Test 4: Filter by priority
    high_tasks = await list_tasks(user_id=test_user, priority=['high'])
    print(f'Tasks with high priority: {len(high_tasks["tasks"])}')

    # Test 5: Filter by tags
    work_tasks = await list_tasks(user_id=test_user, tags=['work'])
    print(f'Tasks with work tag: {len(work_tasks["tasks"])}')

    # Test 6: Search functionality
    search_results = await list_tasks(user_id=test_user, search_term='test')
    print(f'Search results for "test": {len(search_results["tasks"])}')

    print('Basic functionality test completed successfully!')

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())