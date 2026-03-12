#!/usr/bin/env python3
"""
Test script to verify backend-frontend connection
"""

import asyncio
import aiohttp
import subprocess
import time
import signal
import os
import sys

# Add the backend to the Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

async def test_backend_connection():
    """Test if the backend is running and accessible"""
    try:
        async with aiohttp.ClientSession() as session:
            # Test the health endpoint
            async with session.get('http://localhost:8000/health') as resp:
                if resp.status == 200:
                    health_data = await resp.json()
                    print(f"✓ Backend health check passed: {health_data}")
                    return True
                else:
                    print(f"✗ Backend health check failed with status: {resp.status}")
                    return False
    except Exception as e:
        print(f"✗ Backend connection failed: {str(e)}")
        return False

async def test_cors_configuration():
    """Test if CORS is properly configured for frontend origin"""
    try:
        async with aiohttp.ClientSession() as session:
            # Make a request with Origin header to test CORS
            headers = {'Origin': 'http://localhost:5174'}
            async with session.get('http://localhost:8000/health', headers=headers) as resp:
                cors_header = resp.headers.get('Access-Control-Allow-Origin')
                if cors_header == '*' or 'localhost:5174' in cors_header:
                    print(f"✓ CORS configured for frontend origin: {cors_header}")
                    return True
                else:
                    print(f"✗ CORS not properly configured: {cors_header}")
                    return False
    except Exception as e:
        print(f"✗ CORS test failed: {str(e)}")
        return False

async def main():
    print("Testing backend-frontend connection...")
    print("=" * 50)

    # Test backend accessibility
    backend_ok = await test_backend_connection()

    # Test CORS configuration
    cors_ok = await test_cors_configuration()

    print("=" * 50)
    if backend_ok and cors_ok:
        print("✓ All connection tests passed!")
        return True
    else:
        print("✗ Some connection tests failed!")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)