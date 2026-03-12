"""
Live debugging test to identify the exact failure point
"""
import asyncio
import httpx
import json

async def test_both_paths():
    """Test both curl (direct) and browser (proxy) paths"""

    # Test 1: Direct backend call (simulates curl)
    print("=" * 60)
    print("TEST 1: Direct Backend Call (port 8001)")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8001/api/user-test/chat",
                json={"message": "add buy fresh flowers"},
                headers={"Content-Type": "application/json"},
                timeout=10.0
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            print(f"Response JSON: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"ERROR: {e}")

    print("\n")

    # Test 2: Through Vite proxy (simulates browser)
    print("=" * 60)
    print("TEST 2: Through Vite Proxy (port 5174)")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:5174/api/user-test/chat",
                json={"message": "add buy fresh flowers"},
                headers={"Content-Type": "application/json"},
                timeout=10.0
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            print(f"Response JSON: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"ERROR: {e}")

    print("\n")

    # Test 3: Check what the backend actually receives
    print("=" * 60)
    print("TEST 3: Backend Logs Analysis")
    print("=" * 60)
    print("Check your backend terminal for these log lines:")
    print("  [BACKEND LOG] Incoming: POST /api/user-test/chat")
    print("  [FRONTEND REQUEST] POST /api/user-test/chat")
    print("\nIf you see the first but not the second, the issue is in the proxy.")
    print("If you see both, the issue is in the command parser regex.")

if __name__ == "__main__":
    asyncio.run(test_both_paths())
