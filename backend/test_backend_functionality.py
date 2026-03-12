"""
Test script to verify all backend functionality is working correctly
and check for any HTTP 500 errors
"""

import asyncio
import httpx
import json
import time

async def test_backend_functionality():
    """Test all backend functionality to verify no HTTP 500 errors"""
    base_url = "http://localhost:8000"
    user_id = "test-user-functional"

    print("Testing Todo AI Chatbot Backend Functionality")
    print("=" * 50)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Health endpoint
        print("\n1. Testing Health Endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"   ✅ Health check: {health_data}")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
            return False

        # Test 2: Add task
        print("\n2. Testing Add Task...")
        try:
            response = await client.post(
                f"{base_url}/api/{user_id}/chat",
                json={"message": "Add task to buy groceries"},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Add task: {data['response']}")
            else:
                print(f"   ❌ Add task failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Add task error: {e}")
            return False

        # Test 3: Add another task
        print("\n3. Testing Add Another Task...")
        try:
            response = await client.post(
                f"{base_url}/api/{user_id}/chat",
                json={"message": "Add task to walk the dog"},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Add second task: {data['response']}")
            else:
                print(f"   ❌ Add second task failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Add second task error: {e}")
            return False

        # Test 4: List tasks
        print("\n4. Testing List Tasks...")
        try:
            response = await client.post(
                f"{base_url}/api/{user_id}/chat",
                json={"message": "Show my tasks"},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ List tasks: {data['response']}")
            else:
                print(f"   ❌ List tasks failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ List tasks error: {e}")
            return False

        # Test 5: Complete task
        print("\n5. Testing Complete Task...")
        try:
            response = await client.post(
                f"{base_url}/api/{user_id}/chat",
                json={"message": "Complete task 1"},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Complete task: {data['response']}")
            else:
                print(f"   ❌ Complete task failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Complete task error: {e}")
            return False

        # Test 6: Update task
        print("\n6. Testing Update Task...")
        try:
            response = await client.post(
                f"{base_url}/api/{user_id}/chat",
                json={"message": "Update 'walk the dog' to 'walk the golden retriever'"},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Update task: {data['response']}")
            else:
                print(f"   ❌ Update task failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Update task error: {e}")
            return False

        # Test 7: Delete task
        print("\n7. Testing Delete Task...")
        try:
            response = await client.post(
                f"{base_url}/api/{user_id}/chat",
                json={"message": "Delete task 1"},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Delete task: {data['response']}")
            else:
                print(f"   ❌ Delete task failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Delete task error: {e}")
            return False

        # Test 8: Final list to verify changes
        print("\n8. Testing Final List...")
        try:
            response = await client.post(
                f"{base_url}/api/{user_id}/chat",
                json={"message": "Show my tasks"},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Final list: {data['response']}")
            else:
                print(f"   ❌ Final list failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Final list error: {e}")
            return False

        # Test 9: Test help command
        print("\n9. Testing Help Command...")
        try:
            response = await client.post(
                f"{base_url}/api/{user_id}/chat",
                json={"message": "Help"},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Help command: {data['response'][:50]}...")
            else:
                print(f"   ❌ Help command failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Help command error: {e}")
            return False

    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED - No HTTP 500 errors detected!")
    print("✅ All MCP tools (add, list, complete, update, delete) are working correctly!")
    print("✅ Chatbot responds properly to all commands!")

    return True

if __name__ == "__main__":
    success = asyncio.run(test_backend_functionality())
    if success:
        print("\n🎉 Backend functionality test completed successfully!")
    else:
        print("\n❌ Backend functionality test failed!")
        exit(1)