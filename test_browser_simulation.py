"""
CRITICAL: Simulate EXACT browser request to backend
This will reveal if there's a difference between direct calls and browser calls
"""
import asyncio
import httpx
import json
import time

async def test_browser_request():
    """Simulate the exact request a browser makes"""

    print("=" * 70)
    print("BROWSER REQUEST SIMULATION")
    print("=" * 70)
    print()

    # Simulate browser request through proxy
    test_user_id = "test-user-browser-" + str(int(time.time()))
    test_message = "add buy fresh flowers"

    print(f"User ID: {test_user_id}")
    print(f"Message: '{test_message}'")
    print()

    # Test 1: Direct to backend (port 8001)
    print("TEST 1: Direct Backend Call (Port 8001)")
    print("-" * 70)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"http://localhost:8001/api/{test_user_id}/chat",
                json={"message": test_message},
                headers={
                    "Content-Type": "application/json",
                    "Origin": "http://localhost:5174"
                }
            )

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                print(f"Response: {response_text[:200]}...")

                if "Task added" in response_text:
                    print("[PASS] Backend returns success")
                elif "couldn't understand" in response_text:
                    print("[FAIL] Backend returns error message")
                    print(f"Full response: {response_text}")
                else:
                    print("[WARN] Unexpected response")
                    print(f"Full response: {response_text}")
            else:
                print(f"[FAIL] Status {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            print(f"[FAIL] Request failed: {e}")

    print()

    # Test 2: Through proxy (port 5174)
    print("TEST 2: Through Proxy (Port 5174)")
    print("-" * 70)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"http://localhost:5174/api/{test_user_id}/chat",
                json={"message": test_message},
                headers={
                    "Content-Type": "application/json",
                    "Origin": "http://localhost:5174",
                    "Referer": "http://localhost:5174/"
                }
            )

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                print(f"Response: {response_text[:200]}...")

                if "Task added" in response_text:
                    print("[PASS] Proxy returns success")
                elif "couldn't understand" in response_text:
                    print("[FAIL] Proxy returns error message")
                    print(f"Full response: {response_text}")
                else:
                    print("[WARN] Unexpected response")
                    print(f"Full response: {response_text}")
            else:
                print(f"[FAIL] Status {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            print(f"[FAIL] Request failed: {e}")

    print()
    print("=" * 70)
    print("INSTRUCTIONS FOR USER")
    print("=" * 70)
    print()
    print("Now test in your ACTUAL BROWSER:")
    print()
    print("1. Open http://localhost:5174")
    print("2. Press F12 to open DevTools")
    print("3. Go to Network tab")
    print("4. Clear network log (trash icon)")
    print("5. Send message: 'add buy fresh flowers'")
    print("6. Look for request to /api/user-xxx/chat")
    print()
    print("Check:")
    print("- Does the request appear in Network tab?")
    print("- What is the Status Code?")
    print("- What is the Response body?")
    print()
    print("If NO request appears:")
    print("  -> Frontend is blocking the call before fetch()")
    print()
    print("If request appears with Status 200:")
    print("  -> Check Response tab for actual response")
    print("  -> If it says 'Task added' but UI shows error,")
    print("     then frontend is overriding the response")
    print()
    print("If request appears with error status:")
    print("  -> Backend is returning an error")
    print("  -> Check backend terminal for logs")

if __name__ == "__main__":
    asyncio.run(test_browser_request())
