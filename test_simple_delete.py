#!/usr/bin/env python3
"""
Simple test to trigger delete and check logs.
"""

import requests
import time

BASE_URL = "http://localhost:8001/api"

def test_simple_delete():
    """Simple delete test."""

    test_user = f'test-simple-{int(time.time())}'
    endpoint = f'{BASE_URL}/{test_user}/chat'

    print('Adding task...')
    requests.post(endpoint, json={'message': 'add Test Task'}, timeout=20)
    time.sleep(1)

    print('Attempting delete...')
    response = requests.post(endpoint, json={'message': 'delete task 1'}, timeout=20)

    if response.status_code == 200:
        data = response.json()
        resp = data.get('response', '')
        resp_display = resp.encode('ascii', 'ignore').decode('ascii')
        print(f'Response: {resp_display[:200]}')
    else:
        print(f'Error: Status {response.status_code}')

if __name__ == '__main__':
    test_simple_delete()
