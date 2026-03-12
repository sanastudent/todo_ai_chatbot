#!/usr/bin/env python3
"""
Test script to verify OpenRouter API key is loaded and backend is working
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8001/api"
test_user = "test-api-key-check"

def test_backend_health():
    """Test if backend is running"""
    print("1. Testing backend health...")
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is running")
            return True
        else:
            print(f"   ❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Backend is not running on port 8001")
        print("   → Start backend: cd backend && python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_api_key_detection():
    """Test if API key is detected by trying a simple command"""
    print("\n2. Testing API key detection...")
    endpoint = f"{BASE_URL}/{test_user}/chat"

    try:
        # Try a simple command that should work with or without AI
        response = requests.post(
            endpoint,
            json={"message": "add Test task for API key verification"},
            timeout=20
        )

        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')

            # Check if we're getting the "no API key" error
            if "AI natural language processing is not available" in response_text:
                print("   ❌ API key NOT detected - backend is in fallback mode")
                print("   → Backend logs should show: 'No valid API keys configured'")
                return False
            elif "✅" in response_text or "Task added" in response_text:
                print("   ✅ Command executed successfully")
                print(f"   Response: {response_text[:100]}...")
                return True
            else:
                print(f"   ⚠️  Unexpected response: {response_text[:200]}")
                return False
        else:
            print(f"   ❌ Request failed with status {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        print("   ❌ Request timed out (>20s)")
        print("   → This might indicate API is being called but timing out")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_mcp_tools_working():
    """Test if MCP tools are actually being called"""
    print("\n3. Testing MCP tools functionality...")
    endpoint = f"{BASE_URL}/{test_user}/chat"

    try:
        # Add a task
        print("   Testing: add task...")
        response = requests.post(
            endpoint,
            json={"message": "add Buy fresh fruits"},
            timeout=20
        )

        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')

            if "✅" in response_text or "added" in response_text.lower():
                print("   ✅ Add task works")
            else:
                print(f"   ⚠️  Add task response: {response_text[:100]}")

        time.sleep(1)

        # List tasks
        print("   Testing: list tasks...")
        response = requests.post(
            endpoint,
            json={"message": "list tasks"},
            timeout=20
        )

        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')

            if "fresh fruits" in response_text.lower() or "📋" in response_text:
                print("   ✅ List tasks works")
                print(f"   Tasks found: {response_text[:150]}...")
                return True
            else:
                print(f"   ⚠️  List tasks response: {response_text[:100]}")
                return False

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    print("="*60)
    print("OpenRouter API Key & MCP Tools Verification")
    print("="*60)

    # Test 1: Backend health
    if not test_backend_health():
        print("\n❌ FAILED: Backend is not running")
        print("\nFix: Start the backend server:")
        print("  cd backend")
        print("  python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload")
        sys.exit(1)

    # Test 2: API key detection
    api_key_ok = test_api_key_detection()

    # Test 3: MCP tools
    mcp_tools_ok = test_mcp_tools_working()

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Backend Running:     {'✅ YES' if True else '❌ NO'}")
    print(f"API Key Detected:    {'✅ YES' if api_key_ok else '❌ NO'}")
    print(f"MCP Tools Working:   {'✅ YES' if mcp_tools_ok else '❌ NO'}")
    print("="*60)

    if api_key_ok and mcp_tools_ok:
        print("\n🎉 SUCCESS! Everything is working correctly!")
        print("\nYour Todo AI Chatbot is ready to use:")
        print("  - API key is loaded")
        print("  - MCP tools are functioning")
        print("  - Commands are being executed")
        sys.exit(0)
    else:
        print("\n❌ ISSUES DETECTED")
        if not api_key_ok:
            print("\n🔧 Fix API Key Issue:")
            print("  1. Check .env file exists: backend/.env")
            print("  2. Verify OPENROUTER_API_KEY is set")
            print("  3. Restart backend server to load new .env")
        if not mcp_tools_ok:
            print("\n🔧 Fix MCP Tools Issue:")
            print("  1. Check backend logs for errors")
            print("  2. Verify database is accessible")
            print("  3. Check MCP tools are imported correctly")
        sys.exit(1)

if __name__ == "__main__":
    main()
