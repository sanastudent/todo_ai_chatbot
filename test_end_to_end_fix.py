"""
End-to-End Test: Verify Frontend-Backend Communication Fix

This test simulates the exact browser behavior to verify the fix works.
"""
import asyncio
import httpx
import json
import time

async def test_complete_flow():
    """Test the complete user flow after the fix"""

    print("=" * 70)
    print("END-TO-END TEST: Frontend-Backend Communication Fix")
    print("=" * 70)
    print()

    # Test 1: Verify backend is running
    print("TEST 1: Backend Health Check")
    print("-" * 70)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8001/health", timeout=5.0)
            if response.status_code == 200:
                print("✓ Backend is running on port 8001")
                print(f"  Response: {response.json()}")
            else:
                print(f"✗ Backend returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Backend is not running: {e}")
            print("  Please start backend: cd backend && python -m uvicorn src.main:app --port 8001")
            return False

    print()

    # Test 2: Verify frontend proxy is working
    print("TEST 2: Frontend Proxy Health Check")
    print("-" * 70)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:5174/api/health", timeout=5.0)
            if response.status_code == 200:
                print("✓ Frontend proxy is working on port 5174")
                print(f"  Response: {response.json()}")
            else:
                print(f"✗ Frontend proxy returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Frontend is not running: {e}")
            print("  Please start frontend: cd frontend && npm run dev")
            return False

    print()

    # Test 3: Test the actual chat endpoint (simulating browser request)
    print("TEST 3: Chat Endpoint - Add Task")
    print("-" * 70)
    test_user_id = "test-user-" + str(int(time.time()))
    test_message = "add buy fresh flowers"

    async with httpx.AsyncClient() as client:
        try:
            # Simulate browser request through proxy
            response = await client.post(
                f"http://localhost:5174/api/{test_user_id}/chat",
                json={"message": test_message},
                headers={
                    "Content-Type": "application/json",
                    "Origin": "http://localhost:5174"
                },
                timeout=10.0
            )

            print(f"Request: POST /api/{test_user_id}/chat")
            print(f"Message: '{test_message}'")
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')

                print(f"Response length: {len(response_text)} characters")
                print(f"Response preview: {response_text[:100]}...")
                print()

                # Check for success indicators
                success_indicators = [
                    "Task added",
                    "buy fresh flowers",
                    "✅"
                ]

                failures = [
                    "couldn't understand",
                    "AI not available",
                    "Backend is not available"
                ]

                has_success = any(indicator in response_text for indicator in success_indicators)
                has_failure = any(failure in response_text for failure in failures)

                if has_success and not has_failure:
                    print("✓ SUCCESS: Task was added successfully!")
                    print(f"  Full response: {response_text}")
                    return True
                elif has_failure:
                    print("✗ FAILURE: Got error message instead of success")
                    print(f"  Response: {response_text}")
                    print()
                    print("DIAGNOSIS:")
                    print("  The backend is running and responding, but returning an error.")
                    print("  This suggests the command parser or AI agent is failing.")
                    return False
                else:
                    print("⚠ UNEXPECTED: Response doesn't match expected patterns")
                    print(f"  Response: {response_text}")
                    return False
            else:
                print(f"✗ Request failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"  Error: {error_data}")
                except:
                    print(f"  Response: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Request failed: {e}")
            return False

    print()

async def test_direct_backend():
    """Test direct backend access (bypass proxy)"""
    print()
    print("TEST 4: Direct Backend Access (Bypass Proxy)")
    print("-" * 70)

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

            print(f"Request: POST http://localhost:8001/api/{test_user_id}/chat")
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                print(f"Response: {response_text[:100]}...")

                if "Task added" in response_text:
                    print("✓ Direct backend access works correctly")
                    return True
                else:
                    print("✗ Direct backend returned unexpected response")
                    return False
            else:
                print(f"✗ Direct backend failed with status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Direct backend test failed: {e}")
            return False

async def main():
    """Run all tests"""
    print()
    print("This test verifies the frontend-backend communication fix.")
    print("Make sure both backend (port 8001) and frontend (port 5174) are running.")
    print()
    input("Press Enter to start tests...")
    print()

    # Run tests
    proxy_test_passed = await test_complete_flow()
    direct_test_passed = await test_direct_backend()

    # Summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Proxy Test (Browser Simulation): {'✓ PASSED' if proxy_test_passed else '✗ FAILED'}")
    print(f"Direct Backend Test:              {'✓ PASSED' if direct_test_passed else '✗ FAILED'}")
    print()

    if proxy_test_passed and direct_test_passed:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("The fix is working correctly. You can now:")
        print("1. Open browser to http://localhost:5174")
        print("2. Clear browser cache (Ctrl+Shift+Delete)")
        print("3. Login and test: 'add buy fresh flowers'")
        print("4. You should see: '✅ Task added: buy fresh flowers'")
    elif direct_test_passed and not proxy_test_passed:
        print("⚠ PARTIAL SUCCESS")
        print()
        print("Direct backend works, but proxy test failed.")
        print("This suggests a frontend issue. Try:")
        print("1. Restart frontend: cd frontend && npm run dev")
        print("2. Clear browser cache completely")
        print("3. Check browser console for errors (F12)")
    else:
        print("❌ TESTS FAILED")
        print()
        print("Please check:")
        print("1. Backend is running: python -m uvicorn src.main:app --port 8001")
        print("2. Frontend is running: npm run dev (in frontend directory)")
        print("3. No other services using ports 8001 or 5174")

    print()

if __name__ == "__main__":
    asyncio.run(main())
