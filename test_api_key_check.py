#!/usr/bin/env python3
"""
Check if the backend can see the OpenRouter API key.
"""

import os
import sys

# Add backend to path
sys.path.insert(0, 'backend/src')

# Load .env file
from dotenv import load_dotenv
load_dotenv('backend/.env')

# Check API key
api_key = os.getenv("OPENROUTER_API_KEY")

print('='*70)
print('API KEY CHECK')
print('='*70)
print(f'API Key exists: {api_key is not None}')
if api_key:
    print(f'API Key starts with: {api_key[:15]}...')
    print(f'API Key length: {len(api_key)}')
    print(f'Starts with sk-or-: {api_key.startswith("sk-or-")}')
    print(f'Starts with sk-or-v1-: {api_key.startswith("sk-or-v1-")}')
else:
    print('API Key is NOT set')
print('='*70)
