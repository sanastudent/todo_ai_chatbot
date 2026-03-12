#!/usr/bin/env python3
"""
Test specifically for delete operation to see where it fails.
"""

import requests
import time

BASE_URL = "http://localhost:8001/api"

def test_delete_operation():
    """Test delete operation step by step."""

    test_user = f'test-delete-{int(time.time())}'
    endpoint = f'{BASE_URL}/{test_user}/chat'

    print('='*70)
    print('TESTING DELETE OPERATION')
    print('='*70)
    print(f'Test User: {test_user}')
    print()

    # Step 1: Add a task
    print('Step 1: Adding a task...')
    response = requests.post(endpoint, json={'message': 'add Test Task'}, timeout=20)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        resp_display = resp.encode('ascii', 'ignore').decode('ascii')[:100]
        print(f'  Response: {resp_display}')
        print('  [OK] Task added')
    else:
        print(f'  [FAIL] Status {response.status_code}')
        return
    print()

    time.sleep(1)

    # Step 2: List tasks to verify
    print('Step 2: Listing tasks...')
    response = requests.post(endpoint, json={'message': 'list tasks'}, timeout=20)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        resp_display = resp.encode('ascii', 'ignore').decode('ascii')[:150]
        print(f'  Response: {resp_display}')
        print('  [OK] Tasks listed')
    else:
        print(f'  [FAIL] Status {response.status_code}')
        return
    print()

    time.sleep(1)

    # Step 3: Try to delete with different phrasings
    delete_commands = [
        'delete task 1',
        'remove task 1',
        'delete the first task',
        'I want to delete task 1'
    ]

    for i, cmd in enumerate(delete_commands, 1):
        print(f'Step 3.{i}: Trying "{cmd}"...')
        response = requests.post(endpoint, json={'message': cmd}, timeout=20)
        if response.status_code == 200:
            data = response.json()
            resp = data.get('response', '')
            resp_display = resp.encode('ascii', 'ignore').decode('ascii')
            print(f'  Response: {resp_display[:200]}')

            if 'are you sure' in resp.lower() or 'confirm' in resp.lower():
                print('  [SUCCESS] Confirmation requested!')
                return True
            elif 'not available' in resp.lower():
                print('  [FAIL] AI agent not available for this command')
            elif 'deleted' in resp.lower():
                print('  [FAIL] Deleted without confirmation')
            else:
                print('  [UNCLEAR] Unexpected response')
        else:
            print(f'  [FAIL] Status {response.status_code}')
        print()
        time.sleep(1)

    print('='*70)
    print('CONCLUSION: None of the delete commands triggered confirmation')
    print('='*70)

if __name__ == '__main__':
    test_delete_operation()
