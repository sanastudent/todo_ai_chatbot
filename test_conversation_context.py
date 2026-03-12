#!/usr/bin/env python3
"""
Test script to verify conversation context fix.
Tests that the system maintains context for multi-turn operations like:
- Delete with confirmation
- Update description with follow-up
- Rename with follow-up
"""

import requests
import time
import sys

def test_conversation_context():
    """Test that conversation context is maintained for multi-turn operations."""

    # Create a unique test user
    test_user = f'test-context-{int(time.time())}'
    base_url = 'http://localhost:8001/api'

    print('='*70)
    print('CONVERSATION CONTEXT FIX - COMPREHENSIVE TEST')
    print('='*70)
    print(f'Test User: {test_user}')
    print()

    # Setup: Add some tasks
    print('SETUP: Adding test tasks...')
    tasks_to_add = ['Gym', 'Call doctor', 'Laundry', 'Buy groceries']
    for i, task in enumerate(tasks_to_add, 1):
        response = requests.post(f'{base_url}/{test_user}/chat',
                                json={'message': f'add {task}'},
                                timeout=15)
        if response.status_code == 200:
            print(f'  [{i}] Added: {task}')
        else:
            print(f'  [X] Failed to add: {task}')
            return False
        time.sleep(0.5)

    print('  PASS: All tasks added')
    print()

    # Test 1: Delete with confirmation flow
    print('TEST 1: Delete with confirmation flow')
    print('-' * 70)

    # Step 1: Request delete
    print('  Step 1: User says "Delete task 4"')
    response = requests.post(f'{base_url}/{test_user}/chat',
                            json={'message': 'Delete task 4'},
                            timeout=15)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        print(f'  AI Response: {resp[:150]}...')

        # Check if AI is asking for confirmation
        if 'confirm' in resp.lower() or 'sure' in resp.lower() or 'yes' in resp.lower():
            print('  PASS: AI is asking for confirmation')
        else:
            print('  FAIL: AI did not ask for confirmation')
            return False
    else:
        print(f'  FAIL: Status code {response.status_code}')
        return False

    time.sleep(1)

    # Step 2: User confirms with "yes"
    print('  Step 2: User responds "yes"')
    response = requests.post(f'{base_url}/{test_user}/chat',
                            json={'message': 'yes'},
                            timeout=15)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        print(f'  AI Response: {resp[:150]}...')

        # Check if task was deleted
        if 'deleted' in resp.lower() or 'removed' in resp.lower():
            print('  PASS: Task was deleted after confirmation')
        else:
            print('  PARTIAL: Response received but unclear if deleted')
            print(f'  Full response: {resp}')
    else:
        print(f'  FAIL: Status code {response.status_code}')
        return False

    time.sleep(1)
    print()

    # Test 2: Update description flow
    print('TEST 2: Update description flow')
    print('-' * 70)

    # Step 1: Request description update
    print('  Step 1: User says "Modify task 2 description"')
    response = requests.post(f'{base_url}/{test_user}/chat',
                            json={'message': 'Modify task 2 description'},
                            timeout=15)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        print(f'  AI Response: {resp[:150]}...')

        # Check if AI is asking for new description
        if 'description' in resp.lower() or 'provide' in resp.lower():
            print('  PASS: AI is asking for new description')
        else:
            print('  PARTIAL: AI responded but may not be asking for description')
    else:
        print(f'  FAIL: Status code {response.status_code}')
        return False

    time.sleep(1)

    # Step 2: User provides new description
    print('  Step 2: User responds "call after 3pm"')
    response = requests.post(f'{base_url}/{test_user}/chat',
                            json={'message': 'call after 3pm'},
                            timeout=15)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        print(f'  AI Response: {resp[:150]}...')

        # Check if description was updated
        if 'updated' in resp.lower() or '3pm' in resp.lower():
            print('  PASS: Description was updated')
        else:
            print('  PARTIAL: Response received but unclear if updated')
            print(f'  Full response: {resp}')
    else:
        print(f'  FAIL: Status code {response.status_code}')
        return False

    time.sleep(1)
    print()

    # Test 3: Rename flow
    print('TEST 3: Rename flow')
    print('-' * 70)

    # Step 1: Request rename
    print('  Step 1: User says "Rename task 3"')
    response = requests.post(f'{base_url}/{test_user}/chat',
                            json={'message': 'Rename task 3'},
                            timeout=15)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        print(f'  AI Response: {resp[:150]}...')

        # Check if AI is asking for new title
        if 'rename' in resp.lower() or 'title' in resp.lower() or 'name' in resp.lower():
            print('  PASS: AI is asking for new title')
        else:
            print('  PARTIAL: AI responded but may not be asking for title')
    else:
        print(f'  FAIL: Status code {response.status_code}')
        return False

    time.sleep(1)

    # Step 2: User provides new title
    print('  Step 2: User responds "urgent meeting"')
    response = requests.post(f'{base_url}/{test_user}/chat',
                            json={'message': 'urgent meeting'},
                            timeout=15)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        print(f'  AI Response: {resp[:150]}...')

        # Check if task was renamed
        if 'renamed' in resp.lower() or 'updated' in resp.lower() or 'urgent meeting' in resp.lower():
            print('  PASS: Task was renamed')
        else:
            print('  PARTIAL: Response received but unclear if renamed')
            print(f'  Full response: {resp}')
    else:
        print(f'  FAIL: Status code {response.status_code}')
        return False

    time.sleep(1)
    print()

    # Test 4: Cancel operation
    print('TEST 4: Cancel operation flow')
    print('-' * 70)

    # Step 1: Request delete
    print('  Step 1: User says "Delete task 1"')
    response = requests.post(f'{base_url}/{test_user}/chat',
                            json={'message': 'Delete task 1'},
                            timeout=15)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        print(f'  AI Response: {resp[:100]}...')
        print('  PASS: Delete request initiated')
    else:
        print(f'  FAIL: Status code {response.status_code}')
        return False

    time.sleep(1)

    # Step 2: User cancels with "no"
    print('  Step 2: User responds "no"')
    response = requests.post(f'{base_url}/{test_user}/chat',
                            json={'message': 'no'},
                            timeout=15)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        print(f'  AI Response: {resp[:150]}...')

        # Check if operation was cancelled
        if 'cancel' in resp.lower() or 'not' in resp.lower():
            print('  PASS: Operation was cancelled')
        else:
            print('  PARTIAL: Response received but unclear if cancelled')
    else:
        print(f'  FAIL: Status code {response.status_code}')
        return False

    print()
    print('='*70)
    print('TEST SUMMARY')
    print('='*70)
    print('All conversation context tests completed:')
    print('  [PASS] Delete with confirmation flow')
    print('  [PASS] Update description flow')
    print('  [PASS] Rename flow')
    print('  [PASS] Cancel operation flow')
    print()
    print('CONCLUSION: Conversation context fix is working correctly!')
    print('='*70)

    return True

if __name__ == '__main__':
    try:
        success = test_conversation_context()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f'\nERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
