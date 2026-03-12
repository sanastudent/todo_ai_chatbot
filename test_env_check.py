#!/usr/bin/env python3
"""
Test to verify environment variables are loaded correctly.
"""

import requests

BASE_URL = "http://localhost:8001/api"

def test_env_check():
    """Send a test message to check if AI is working."""

    test_user = 'test-env-check'
    endpoint = f'{BASE_URL}/{test_user}/chat'

    print('Testing if AI agent is available...')
    response = requests.post(endpoint, json={'message': 'hello'}, timeout=20)

    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        resp_display = resp.encode('ascii', 'ignore').decode('ascii')
        print(f'Response: {resp_display}')

        if 'not available' in resp.lower() or 'no api key' in resp.lower():
            print('\nPROBLEM: AI agent is NOT available')
            print('The OpenRouter API key is not being recognized')
        else:
            print('\nSUCCESS: AI agent is working')
    else:
        print(f'ERROR: Status {response.status_code}')

if __name__ == '__main__':
    test_env_check()
