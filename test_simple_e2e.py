"""
Simple End-to-End Test (Windows Compatible)
Tests the frontend-backend communication fix without Unicode characters
"""
import asyncio
import httpx
import json
import time

async def test_backend_health():
    """Test if backend is running"""
    print("TEST 1: Backend Health Check")
    print("-" * 60)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8001/health", timeout=5.0)
            if response.status_code == 200:
                print("[PASS] Backend is running on port 8001")
                return True
            else:
                print(f"[FAIL] Backend returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"[FAIL] Backend is not running: {e}")
            return False

async def test_frontend_proxy():
    """Test if frontend proxy is working"""
    print("\nTEST 2: Frontend Proxy Health Check")
    print("-" * 60)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:5174/api/health", timeout=5.0)
            if response.status_code == 200:
                print("[PASS] Frontend proxy is working on port 5174")
                return True
            else:
                print(f"[FAIL] Frontend proxy returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"[FAIL] Frontend is not running: {e}")
            return False

async def test_chat_endpoint():
    """Test the actual chat endpoint through proxy"""
    print("\nTEST 3: Chat Endpoint - Add Task (Through Proxy)")
    print("-" * 60)

    test_user_id = "test-user-" + str(int(time.time()))
    test_message = "add buy fresh flowers"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"http://localhost:5174/api/{test_user_id}/chat",
                json={"message": test_message},
                headers={"Content-Type": "application/json"},
                timeout=10.0
            )

            print(f"Request: POST /api/{test_user_id}/chat")
            print(f"Message: '{test_message}'")
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')

                print(f"Response length: {len(response_text)} characters")

                # Check for success
                if "Task added" in response_text and "buy fresh flowers" in response_text:
                    print("[PASS] Task was added successfully!")
                    print(f"Response: {response_text}")
                    return True
                elif "couldn't understand" in response_text or "AI not available" in response_text:
                    print("[FAIL] Got error message instead of success")
                    print(f"Response: {response_text}")
                    return False
                else:
                    print("[WARN] Unexpected response")
                    print(f"Response: {response_text}")
                    return False
            else:
                print(f"[FAIL] Request failed with status {response.status_code}")
                return False
        except Exception as e:
            print(f"[FAIL] Request failed: {e}")
            return False

async def test_direct_backend():
    """Test direct backend access (bypass proxy)"""
    print("\nTEST 4: Direct Backend Access (Bypass Proxy)")
    print("-" * 60)

    test_user_id = "test-user-direct-" + str(int(time.time()))
    test_message = "add buy fresh flowers"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"http://localhost:8001/api/{test_user_id}/chat",
                json={"message": test_message},
                headers={"Content-Type": "application/json"},
                timeout=10.0
            )

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')

                if "Task added" in response_text:
                    print("[PASS] Direct backend access works correctly")
                    print(f"Response: {response_text}")
                    return True
                else:
                    print("[FAIL] Unexpected response from backend")
                    return False
            else:
                print(f"[FAIL] Direct backend failed with status {response.status_code}")
                return False
        except Exception as e:
            print(f"[FAIL] Direct backend test failed: {e}")
            return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("END-TO-END TEST: Frontend-Backend Communication Fix")
    print("=" * 60)
    print()

    # Run tests
    backend_ok = await test_backend_health()
    if not backend_ok:
        print("\n[ERROR] Backend is not running. Please start it first.")
        print("Command: cd backend && python -m uvicorn src.main:app --port 8001")
        return

    frontend_ok = await test_frontend_proxy()
    if not frontend_ok:
        print("\n[ERROR] Frontend is not running. Please start it first.")
        print("Command: cd frontend && npm run dev")
        return

    proxy_test = await test_chat_endpoint()
    direct_test = await test_direct_backend()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Backend Health:     {'[PASS]' if backend_ok else '[FAIL]'}")
    print(f"Frontend Proxy:     {'[PASS]' if frontend_ok else '[FAIL]'}")
    print(f"Proxy Chat Test:    {'[PASS]' if proxy_test else '[FAIL]'}")
    print(f"Direct Backend Test: {'[PASS]' if direct_test else '[FAIL]'}")
    print()

    if proxy_test and direct_test:
        print("SUCCESS! All tests passed.")
        print()
        print("The fix is working. Next steps:")
        print("1. Open browser to http://localhost:5174")
        print("2. Press Ctrl+Shift+Delete to clear cache")
        print("3. Login and test: 'add buy fresh flowers'")
        print("4. You should see success message")
    elif direct_test and not proxy_test:
        print("PARTIAL SUCCESS")
        print()
        print("Direct backend works, but proxy test failed.")
        print("Try restarting the frontend:")
        print("  cd frontend && npm run dev")
    else:
        print("TESTS FAILED")
        print()
        print("Please verify both services are running.")

if __name__ == "__main__":
    asyncio.run(main())
