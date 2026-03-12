#!/usr/bin/env python3
"""
Diagnostic test for conversation context issues.
This will help identify exactly where the conversation context is breaking.
"""

import requests
import time

BASE_URL = "http://localhost:8001/api"

def test_conversation_context_diagnostic():
    """Detailed diagnostic test for conversation context."""

    test_user = f'diagnostic-{int(time.time())}'
    endpoint = f'{BASE_URL}/{test_user}/chat'

    print('='*70)
    print('CONVERSATION CONTEXT DIAGNOSTIC TEST')
    print('='*70)
    print(f'Test User: {test_user}')
    print()

    # Setup: Add a task
    print('SETUP: Adding a test task...')
    response = requests.post(endpoint, json={'message': 'add Test Task'}, timeout=20)
    if response.status_code == 200:
        data = response.json()
        print(f'  Response: {data.get("response", "")[:100]}')
        print(f'  Conversation ID: {data.get("conversation_id", "N/A")}')
        conversation_id = data.get("conversation_id")
    else:
        print(f'  FAIL: Status {response.status_code}')
        return

    time.sleep(1)
    print()

    # Test 1: Delete with confirmation
    print('TEST 1: Delete with Confirmation')
    print('-'*70)

    # Step 1: Request delete
    print('Step 1: User says "delete task 1"')
    response = requests.post(endpoint, json={'message': 'delete task 1'}, timeout=20)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        print(f'  AI Response: {resp}')
        print()

        # Analyze the response
        if 'confirm' in resp.lower() or 'sure' in resp.lower() or 'yes' in resp.lower():
            print('  ANALYSIS: AI is asking for confirmation (GOOD)')
        else:
            print('  ANALYSIS: AI is NOT asking for confirmation (BAD)')
            print('  This suggests pending operation was set but AI did not relay it')

        # Check if response mentions the task
        if 'Test Task' in resp or 'test task' in resp.lower():
            print('  ANALYSIS: AI mentioned the task name (GOOD)')
        else:
            print('  ANALYSIS: AI did not mention task name (NEUTRAL)')
    else:
        print(f'  FAIL: Status {response.status_code}')
        return

    time.sleep(2)
    print()

    # Step 2: Confirm with "yes"
    print('Step 2: User responds "yes"')
    response = requests.post(endpoint, json={'message': 'yes'}, timeout=20)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        print(f'  AI Response: {resp}')
        print()

        # Analyze the response
        if 'deleted' in resp.lower() or 'removed' in resp.lower():
            print('  ANALYSIS: Task was deleted (GOOD)')
        elif 'assist' in resp.lower() or 'help' in resp.lower():
            print('  ANALYSIS: AI lost context - generic response (BAD)')
            print('  This suggests pending operation was not retrieved or cleared prematurely')
        else:
            print('  ANALYSIS: Response unclear')
    else:
        print(f'  FAIL: Status {response.status_code}')
        return

    time.sleep(1)
    print()

    # Verify task was actually deleted
    print('VERIFICATION: Checking if task was actually deleted...')
    response = requests.post(endpoint, json={'message': 'list all tasks'}, timeout=20)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')

        if 'Test Task' in resp or 'test task' in resp.lower():
            print('  RESULT: Task still exists (NOT DELETED)')
        elif 'no tasks' in resp.lower() or 'empty' in resp.lower():
            print('  RESULT: Task was deleted (SUCCESS)')
        else:
            print(f'  RESULT: Unclear - Response: {resp[:100]}')

    print()
    print('='*70)
    print('DIAGNOSTIC COMPLETE')
    print('='*70)

if __name__ == '__main__':
    test_conversation_context_diagnostic()
