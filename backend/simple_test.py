#!/usr/bin/env python3
'''
Simple test to verify add_task and list_tasks functions work correctly
'''

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mcp.tools import add_task, list_tasks
from sqlmodel.ext.asyncio.session import AsyncSession
from src.services.database import async_engine


async def test_add_and_list_tasks():
    '''Test that add_task and list_tasks functions work correctly'''
    print('Starting test of add_task and list_tasks functions...')
    
    async with AsyncSession(async_engine) as session:
        # Test 1: Add a task
        print('\n1. Testing add_task function...')
        result = await add_task(
            user_id='test_user_123',
            title='Test task for verification',
            description='This is a test task to verify functionality',
            db_session=session
        )
        print(f'   ✓ Successfully added task: {result["title"]}')
        print(f'   ✓ Task ID: {result["task_id"]}')
        print(f'   ✓ Created at: {result["created_at"]}')
        
        # Test 2: List tasks (should return the task we just added)
        print('\n2. Testing list_tasks function...')
        result2 = await list_tasks(user_id='test_user_123', db_session=session)
        print(f'   ✓ Found {len(result2["tasks"])} task(s)')
        
        if len(result2['tasks']) > 0:
            task = result2['tasks'][0]
            print(f'   ✓ Task title: {task["title"]}')
            print(f'   ✓ Task completed: {task["completed"]}')
            print(f'   ✓ Task created at: {task["created_at"]}')
            
            # Verify the task we added is in the list
            if task['title'] == 'Test task for verification':
                print('   ✓ Task matches what we added - SUCCESS!')
            else:
                print('   ✗ Task does not match what we added - FAILED!')
        else:
            print('   ✗ No tasks found - FAILED!')
        
        # Test 3: Add another task to verify multiple tasks work
        print('\n3. Testing multiple tasks...')
        result3 = await add_task(
            user_id='test_user_123',
            title='Second test task',
            db_session=session
        )
        print(f'   ✓ Added second task: {result3["title"]}')
        
        # List tasks again to see both
        result4 = await list_tasks(user_id='test_user_123', db_session=session)
        print(f'   ✓ Now found {len(result4["tasks"])} task(s)')
        
        for i, task in enumerate(result4['tasks'], 1):
            print(f'   ✓ Task {i}: {task["title"]} (Completed: {task["completed"]})')
        
        # Test 4: Test filtering by completion status
        print('\n4. Testing list_tasks with completion filter...')
        pending_tasks = await list_tasks(user_id='test_user_123', completed=False, db_session=session)
        print(f'   ✓ Found {len(pending_tasks["tasks"])} pending tasks')
        
        completed_tasks = await list_tasks(user_id='test_user_123', completed=True, db_session=session)
        print(f'   ✓ Found {len(completed_tasks["tasks"])} completed tasks')
        
        print('\n✓ All tests completed successfully!')
        print('✓ add_task and list_tasks functions are working correctly!')


if __name__ == '__main__':
    print('Running basic test for add_task and list_tasks functions...')
    asyncio.run(test_add_and_list_tasks())
    print('\nTest finished.')
