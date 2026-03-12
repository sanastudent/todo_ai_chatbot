#!/usr/bin/env python3
"""
Test with detailed request/response logging to understand the flow.
"""

import requests
import time
import json

BASE_URL = "http://localhost:8001/api"

def test_with_logging():
    """Test delete with detailed logging."""

    test_user = f'test-log-{int(time.time())}'
    endpoint = f'{BASE_URL}/{test_user}/chat'

    print('='*70)
    print('DETAILED LOGGING TEST')
    print('='*70)
    print(f'Test User: {test_user}')
    print()

    # Add a task
    print('Step 1: Adding a task...')
    response = requests.post(endpoint, json={'message': 'add Debug Task'}, timeout=20)
    print(f'  Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'  Response keys: {list(data.keys())}')
        resp = data.get('response', '')
        print(f'  Response length: {len(resp)} chars')
        resp_display = resp.encode('ascii', 'ignore').decode('ascii')[:200]
        print(f'  Response preview: {resp_display}')
    print()

    time.sleep(1)

    # Try to delete
    print('Step 2: Requesting delete task 1...')
    print('  Sending: {"message": "delete task 1"}')
    response = requests.post(endpoint, json={'message': 'delete task 1'}, timeout=20)
    print(f'  Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'  Response keys: {list(data.keys())}')
        resp = data.get('response', '')
        print(f'  Response length: {len(resp)} chars')
        resp_display = resp.encode('ascii', 'ignore').decode('ascii')
        print(f'  Full response: {resp_display}')
        print()

        # Analyze
        if 'are you sure' in resp.lower() or 'confirm' in resp.lower():
            print('  RESULT: Confirmation requested (GOOD)')
        elif 'deleted' in resp.lower():
            print('  RESULT: Deleted immediately (BAD - using fallback parser)')
        else:
            print('  RESULT: Unclear response')
    else:
        print(f'  ERROR: Status {response.status_code}')
        print(f'  Response: {response.text}')

if __name__ == '__main__':
    test_with_logging()
