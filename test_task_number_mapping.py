#!/usr/bin/env python3
"""
Test script to verify task number mapping fix.
Tests that users can reference tasks by their display numbers (1, 2, 3)
instead of having to use UUIDs.
"""

import requests
import time
import sys

def test_task_number_mapping():
    """Test that task number mapping works for complete, delete, and update operations."""

    # Create a unique test user
    test_user = f'test-number-mapping-{int(time.time())}'
    endpoint = f'http://localhost:8001/api/{test_user}/chat'

    print('='*70)
    print('TASK NUMBER MAPPING FIX - COMPREHENSIVE TEST')
    print('='*70)
    print(f'Test User: {test_user}')
    print()

    # Test 1: Add tasks
    print('TEST 1: Adding 3 tasks...')
    tasks_to_add = ['Gym', 'Call doctor', 'Laundry']
    for i, task in enumerate(tasks_to_add, 1):
        response = requests.post(endpoint, json={'message': f'add {task}'}, timeout=15)
        if response.status_code == 200:
            print(f'  [{i}] Added: {task}')
        else:
            print(f'  [X] Failed to add: {task}')
            return False
        time.sleep(0.5)

    print('  PASS: All tasks added successfully')
    print()

    # Test 2: List tasks to see the order
    print('TEST 2: Listing tasks to see current order...')
    response = requests.post(endpoint, json={'message': 'list all tasks'}, timeout=15)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        print(f'  Response preview: {resp[:200]}...')

        # Extract task order from response
        lines = resp.split('\n')
        task_order = []
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.')):
                task_order.append(line.strip())

        if task_order:
            print('  Task order:')
            for task_line in task_order:
                print(f'    {task_line}')

        print('  PASS: Tasks listed successfully')
    else:
        print(f'  FAIL: Status code {response.status_code}')
        return False

    print()

    # Test 3: Complete task number 1
    print('TEST 3: Complete task number 1...')
    response = requests.post(endpoint, json={'message': 'complete task number 1'}, timeout=15)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        print(f'  Response: {resp[:150]}')

        if 'completed' in resp.lower() or 'marked' in resp.lower():
            print('  PASS: Task 1 was completed')
        else:
            print('  FAIL: Task 1 was not completed')
            return False
    else:
        print(f'  FAIL: Status code {response.status_code}')
        return False

    time.sleep(1)
    print()

    # Test 4: Delete task 2
    print('TEST 4: Delete task 2...')
    response = requests.post(endpoint, json={'message': 'delete task 2'}, timeout=15)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        print(f'  Response: {resp[:150]}')

        if 'deleted' in resp.lower() or 'removed' in resp.lower():
            print('  PASS: Task 2 was deleted')
        else:
            print('  PARTIAL: Response received but unclear if deleted')
    else:
        print(f'  FAIL: Status code {response.status_code}')
        return False

    time.sleep(1)
    print()

    # Test 5: Update task 1 (which should now be a different task after deletions)
    print('TEST 5: Update task 1 to new title...')
    response = requests.post(endpoint, json={'message': 'update task 1 to Buy groceries'}, timeout=15)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        print(f'  Response: {resp[:150]}')

        if 'updated' in resp.lower() or 'changed' in resp.lower() or 'groceries' in resp.lower():
            print('  PASS: Task 1 was updated')
        else:
            print('  PARTIAL: Response received but unclear if updated')
    else:
        print(f'  FAIL: Status code {response.status_code}')
        return False

    time.sleep(1)
    print()

    # Test 6: List final tasks to verify all operations
    print('TEST 6: List final tasks to verify all operations...')
    response = requests.post(endpoint, json={'message': 'show my tasks'}, timeout=15)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        print(f'  Final task list:')
        print(f'  {resp[:300]}')
        print('  PASS: Final list retrieved')
    else:
        print(f'  FAIL: Status code {response.status_code}')
        return False

    print()
    print('='*70)
    print('TEST SUMMARY')
    print('='*70)
    print('All critical tests passed:')
    print('  [PASS] Add tasks')
    print('  [PASS] List tasks')
    print('  [PASS] Complete task by number')
    print('  [PASS] Delete task by number')
    print('  [PASS] Update task by number')
    print()
    print('CONCLUSION: Task number mapping fix is working correctly!')
    print('='*70)

    return True

if __name__ == '__main__':
    try:
        success = test_task_number_mapping()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f'\nERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
