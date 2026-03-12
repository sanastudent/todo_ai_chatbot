#!/usr/bin/env python3
"""
Test the conversation context fix for confirmation messages.
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8001/api"

def test_confirmation_fix():
    """Test that confirmation messages are now shown to the user."""

    test_user = f'test-confirm-{int(time.time())}'
    endpoint = f'{BASE_URL}/{test_user}/chat'

    print('='*70)
    print('TESTING CONFIRMATION FIX')
    print('='*70)
    print(f'Test User: {test_user}')
    print()

    # Step 1: Add a task
    print('Step 1: Adding a test task...')
    response = requests.post(endpoint, json={'message': 'add Test Task for Deletion'}, timeout=20)
    if response.status_code == 200:
        data = response.json()
        resp_text = data.get("response", "")
        # Remove emoji and special characters for display
        resp_display = resp_text.encode('ascii', 'ignore').decode('ascii')
        print(f'  Response: {resp_display[:100]}')
        print('  [OK] Task added')
    else:
        print(f'  [FAIL] Status {response.status_code}')
        return False

    time.sleep(1)
    print()

    # Step 2: Request delete (should ask for confirmation)
    print('Step 2: Requesting delete task 1...')
    response = requests.post(endpoint, json={'message': 'delete task 1'}, timeout=20)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        # Remove emoji for display
        resp_display = resp.encode('ascii', 'ignore').decode('ascii')
        print(f'  Response: {resp_display}')
        print()

        # Check for confirmation keywords
        confirmation_keywords = ['are you sure', 'confirm', 'yes', 'no', 'cancel']
        has_confirmation = any(keyword in resp.lower() for keyword in confirmation_keywords)

        if has_confirmation:
            print('  [SUCCESS] AI is asking for confirmation!')
            print('  The fix is working - confirmation message reached the user')
        else:
            print('  [FAIL] AI is NOT asking for confirmation')
            print('  The fix did not work as expected')
            return False
    else:
        print(f'  [FAIL] Status {response.status_code}')
        return False

    time.sleep(1)
    print()

    # Step 3: Confirm with "yes"
    print('Step 3: Confirming with "yes"...')
    response = requests.post(endpoint, json={'message': 'yes'}, timeout=20)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        resp_display = resp.encode('ascii', 'ignore').decode('ascii')
        print(f'  Response: {resp_display}')
        print()

        if 'deleted' in resp.lower() or 'removed' in resp.lower():
            print('  [SUCCESS] Task was deleted after confirmation!')
            print('  Multi-turn conversation context is working!')
        else:
            print('  [FAIL] Task was not deleted')
            print('  Context may have been lost')
            return False
    else:
        print(f'  [FAIL] Status {response.status_code}')
        return False

    print()
    print('='*70)
    print('TEST COMPLETE - ALL CHECKS PASSED')
    print('='*70)
    return True

if __name__ == '__main__':
    success = test_confirmation_fix()
    sys.exit(0 if success else 1)
