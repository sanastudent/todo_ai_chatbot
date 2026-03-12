import asyncio
import aiohttp
import json

async def test_full_workflow():
    """Test the complete workflow from frontend to backend"""
    print("=== Testing Full Workflow ===\n")

    async with aiohttp.ClientSession() as session:
        user_id = "full-workflow-test"

        # Test 1: Add a task
        print("1. Adding a task...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Add task to buy milk"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result and 'buy milk' in result['response']:
                print(f"   [SUCCESS] {result['response']}")
            else:
                print(f"   [ERROR] Unexpected response: {result}")
        else:
            print(f"   [ERROR] {response.status} - {await response.text()}")

        # Test 2: Add another task
        print("\n2. Adding another task...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Add task to call mom"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result and 'call mom' in result['response']:
                print(f"   [SUCCESS] {result['response']}")
            else:
                print(f"   [ERROR] Unexpected response: {result}")
        else:
            print(f"   [ERROR] {response.status} - {await response.text()}")

        # Test 3: List all tasks
        print("\n3. Listing all tasks...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result and '2 tasks' in result['response']:
                print(f"   [SUCCESS] {result['response']}")
            else:
                print(f"   [ERROR] Unexpected response: {result}")
        else:
            print(f"   [ERROR] {response.status} - {await response.text()}")

        # Test 4: Complete a task by number
        print("\n4. Completing task 1...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Complete task 1"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result and ('completed' in result['response'] or 'marked' in result['response']):
                print(f"   [SUCCESS] {result['response']}")
            else:
                print(f"   [ERROR] Unexpected response: {result}")
        else:
            print(f"   [ERROR] {response.status} - {await response.text()}")

        # Test 5: List tasks to see completion
        print("\n5. Listing tasks after completion...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   [SUCCESS] {result['response']}")
            else:
                print(f"   [ERROR] Unexpected response: {result}")
        else:
            print(f"   [ERROR] {response.status} - {await response.text()}")

        # Test 6: Show completed tasks
        print("\n6. Showing completed tasks...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show completed tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   [SUCCESS] {result['response']}")
            else:
                print(f"   [ERROR] Unexpected response: {result}")
        else:
            print(f"   [ERROR] {response.status} - {await response.text()}")

        # Test 7: Show pending tasks
        print("\n7. Showing pending tasks...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show pending tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   [SUCCESS] {result['response']}")
            else:
                print(f"   [ERROR] Unexpected response: {result}")
        else:
            print(f"   [ERROR] {response.status} - {await response.text()}")

        # Test 8: Delete a task
        print("\n8. Deleting a task...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Delete task 1"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result and ('deleted' in result['response'] or 'removed' in result['response']):
                print(f"   [SUCCESS] {result['response']}")
            else:
                print(f"   [ERROR] Unexpected response: {result}")
        else:
            print(f"   [ERROR] {response.status} - {await response.text()}")

        # Test 9: Final list
        print("\n9. Final task list...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   [SUCCESS] {result['response']}")
            else:
                print(f"   [ERROR] Unexpected response: {result}")
        else:
            print(f"   [ERROR] {response.status} - {await response.text()}")

        # Test 10: Natural language understanding
        print("\n10. Testing natural language understanding...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "What can you help me with?"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   [SUCCESS] {result['response'][:100]}...")
            else:
                print(f"   [ERROR] Unexpected response: {result}")
        else:
            print(f"   [ERROR] {response.status} - {await response.text()}")

        print("\n=== Full workflow test completed ===")


if __name__ == "__main__":
    asyncio.run(test_full_workflow())