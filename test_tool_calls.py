#!/usr/bin/env python3
"""
Test to trigger AI agent with tool calls and capture detailed response.
"""

import requests
import time

BASE_URL = "http://localhost:8001/api"

def test_tool_call():
    """Test if AI agent can handle tool calls."""

    test_user = f'test-tool-{int(time.time())}'
    endpoint = f'{BASE_URL}/{test_user}/chat'

    print('='*70)
    print('TESTING AI AGENT WITH TOOL CALLS')
    print('='*70)
    print(f'Test User: {test_user}')
    print()

    # Test 1: Simple message (no tool call)
    print('Test 1: Simple message (no tool call)...')
    response = requests.post(endpoint, json={'message': 'hello'}, timeout=20)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        resp_display = resp.encode('ascii', 'ignore').decode('ascii')[:100]
        print(f'  Response: {resp_display}')
        if 'not available' in resp.lower():
            print('  [FAIL] AI agent not available')
        else:
            print('  [OK] AI agent working for simple messages')
    print()

    time.sleep(1)

    # Test 2: Message requiring tool call (add task)
    print('Test 2: Message requiring tool call (add task)...')
    response = requests.post(endpoint, json={'message': 'add Buy Milk'}, timeout=20)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        resp_display = resp.encode('ascii', 'ignore').decode('ascii')[:150]
        print(f'  Response: {resp_display}')
        if 'not available' in resp.lower():
            print('  [FAIL] AI agent failing for tool calls')
        elif 'added' in resp.lower() or 'buy milk' in resp.lower():
            print('  [OK] AI agent working for tool calls')
        else:
            print('  [UNCLEAR] Response unclear')
    print()

    time.sleep(1)

    # Test 3: List tasks (another tool call)
    print('Test 3: List tasks (another tool call)...')
    response = requests.post(endpoint, json={'message': 'show my tasks'}, timeout=20)
    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        resp_display = resp.encode('ascii', 'ignore').decode('ascii')[:150]
        print(f'  Response: {resp_display}')
        if 'not available' in resp.lower():
            print('  [FAIL] AI agent failing for tool calls')
        elif 'buy milk' in resp.lower() or 'task' in resp.lower():
            print('  [OK] AI agent working for tool calls')
        else:
            print('  [UNCLEAR] Response unclear')
    print()

    print('='*70)
    print('CONCLUSION:')
    print('If Test 1 passes but Test 2/3 fail, the issue is with tool calling')
    print('If all tests fail, the issue is with the AI agent itself')
    print('='*70)

if __name__ == '__main__':
    test_tool_call()
