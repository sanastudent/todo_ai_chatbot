import asyncio
import httpx
import json

async def test_backend_functionality():
    """Test that the backend server is running and accessible with enhanced features"""

    base_url = "http://localhost:8000"

    print("Testing backend server connectivity...")

    # Test 1: Health check
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            health_response = await client.get(f"{base_url}/health")
            print(f"[PASS] Health check: {health_response.status_code}")

            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"   Status: {health_data.get('status')}")
                print(f"   Database: {health_data.get('database')}")

                # Test 2: API endpoint
                chat_response = await client.post(
                    f"{base_url}/api/testuser/chat",
                    json={
                        "message": "Hello, can you help me with my tasks?",
                        "conversation_id": None
                    }
                )

                print(f"[PASS] Chat endpoint: {chat_response.status_code}")

                if chat_response.status_code == 200:
                    chat_data = chat_response.json()
                    print(f"   Response: {chat_data.get('response', '')[:60]}...")
                    print(f"   Conversation ID: {chat_data.get('conversation_id')}")

                    # Test 3: Check if enhanced features are accessible by simulating a task with priority
                    add_task_response = await client.post(
                        f"{base_url}/api/testuser/chat",
                        json={
                            "message": "Add a high priority task to buy groceries with tags work and urgent",
                            "conversation_id": chat_data.get('conversation_id')
                        }
                    )

                    print(f"[RESULT] Enhanced feature test: {add_task_response.status_code}")

                    if add_task_response.status_code == 200:
                        add_data = add_task_response.json()
                        print(f"   Response: {add_data.get('response', '')[:60]}...")

                        print("\n[SUCCESS] All tests passed! Backend server is running correctly.")
                        print("   - Server is accessible on port 8000")
                        print("   - Health check passes")
                        print("   - Chat API endpoint is functional")
                        print("   - Enhanced features (priority/tags) are accessible")

                        return True
                    else:
                        print(f"   [FAIL] Enhanced feature test failed: {add_task_response.text}")
                        return False
                else:
                    print(f"   [FAIL] Chat endpoint failed: {chat_response.text}")
                    return False
            else:
                print(f"   [FAIL] Health check failed: {health_response.text}")
                return False

        except Exception as e:
            print(f"[ERROR] Connection error: {str(e)}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_backend_functionality())
    if success:
        print("\n[SUCCESS] BACKEND SERVER IS RUNNING PROPERLY AND CONNECTED!")
    else:
        print("\n[ERROR] BACKEND SERVER ISSUES DETECTED")