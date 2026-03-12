#!/usr/bin/env python3
"""
Debug script to check if AI agent is being used or if it's falling back to command parser.
"""

import requests
import time

BASE_URL = "http://localhost:8001/api"

def test_ai_agent_usage():
    """Test if the AI agent is actually being called."""

    test_user = f'test-ai-{int(time.time())}'
    endpoint = f'{BASE_URL}/{test_user}/chat'

    print('='*70)
    print('TESTING AI AGENT USAGE')
    print('='*70)
    print(f'Test User: {test_user}')
    print()

    # Test 1: Send a message that requires AI (not a basic command)
    print('Test 1: Sending a message that requires AI understanding...')
    response = requests.post(endpoint, json={'message': 'What can you help me with?'}, timeout=20)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        resp_display = resp.encode('ascii', 'ignore').decode('ascii')
        print(f'  Response: {resp_display}')
        print()

        # Check if response indicates AI is working
        if 'task' in resp.lower() and ('add' in resp.lower() or 'manage' in resp.lower()):
            print('  [OK] AI agent appears to be working')
        elif 'not available' in resp.lower() or 'no api key' in resp.lower():
            print('  [PROBLEM] AI agent is NOT available - using fallback')
            print('  This explains why confirmation is not working')
            return False
        else:
            print('  [UNCLEAR] Response does not clearly indicate AI status')
    else:
        print(f'  [FAIL] Status {response.status_code}')
        return False

    time.sleep(1)
    print()

    # Test 2: Add a task and try to delete it
    print('Test 2: Adding a task...')
    response = requests.post(endpoint, json={'message': 'add Test Task'}, timeout=20)
    if response.status_code == 200:
        print('  [OK] Task added')
    else:
        print(f'  [FAIL] Status {response.status_code}')
        return False

    time.sleep(1)
    print()

    print('Test 3: Requesting delete (checking for confirmation)...')
    response = requests.post(endpoint, json={'message': 'delete task 1'}, timeout=20)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        resp_display = resp.encode('ascii', 'ignore').decode('ascii')
        print(f'  Response: {resp_display}')
        print()

        # Analyze the response
        if 'are you sure' in resp.lower() or 'confirm' in resp.lower():
            print('  [SUCCESS] Confirmation is being requested!')
            print('  AI agent is working correctly')
            return True
        elif 'deleted' in resp.lower():
            print('  [PROBLEM] Task was deleted immediately without confirmation')
            print('  This indicates the basic command parser is being used')
            print('  AI agent is likely not available or failing')
            return False
        else:
            print('  [UNCLEAR] Response does not match expected patterns')
            return False
    else:
        print(f'  [FAIL] Status {response.status_code}')
        return False

if __name__ == '__main__':
    test_ai_agent_usage()
