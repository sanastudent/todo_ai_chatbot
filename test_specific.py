import asyncio
import aiohttp
import json

async def test_specific_features():
    """Test specific features to identify issues"""
    user_id = "test-user-specific"

    print("=== Testing Specific Features ===\n")

    async with aiohttp.ClientSession() as session:
        # Test 1: Add a task
        print("1. Adding a task...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Add task to buy groceries"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   SUCCESS: {result['response']}")
            else:
                print(f"   ERROR: Unexpected response format: {result}")
        else:
            print(f"   ERROR: Failed with status {response.status}")
            print(await response.text())

        # Test 2: Add the same task again (test duplicate prevention)
        print("\n2. Adding the same task again (testing duplicate prevention)...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Add task to buy groceries"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   RESPONSE: {result['response']}")
                if "already in your tasks" in result['response']:
                    print("   SUCCESS: Duplicate prevention working!")
                else:
                    print("   ISSUE: Duplicate prevention not working")
            else:
                print(f"   ERROR: Unexpected response format: {result}")
        else:
            print(f"   ERROR: Failed with status {response.status}")
            print(await response.text())

        # Test 3: List tasks to see current state
        print("\n3. Listing all tasks...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   TASKS: {result['response']}")
            else:
                print(f"   ERROR: Unexpected response format: {result}")
        else:
            print(f"   ERROR: Failed with status {response.status}")
            print(await response.text())

        # Test 4: Add another task to have multiple tasks
        print("\n4. Adding another task...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Add task to walk the dog"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   SUCCESS: {result['response']}")
            else:
                print(f"   ERROR: Unexpected response format: {result}")
        else:
            print(f"   ERROR: Failed with status {response.status}")
            print(await response.text())

        # Test 5: Try to complete task by number - this is what was failing
        print("\n5. Trying to complete task 1...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Complete task 1"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   RESPONSE: {result['response']}")
                if "marked as completed" in result['response']:
                    print("   SUCCESS: Task completion by number working!")
                else:
                    print("   ISSUE: Task completion by number not working")
            else:
                print(f"   ERROR: Unexpected response format: {result}")
        else:
            print(f"   ERROR: Failed with status {response.status}")
            print(await response.text())

        # Test 6: Try to complete task by #number
        print("\n6. Trying to complete task #1...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Complete task #1"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   RESPONSE: {result['response']}")
                if "marked as completed" in result['response']:
                    print("   SUCCESS: Task completion by #number working!")
                else:
                    print("   ISSUE: Task completion by #number not working")
            else:
                print(f"   ERROR: Unexpected response format: {result}")
        else:
            print(f"   ERROR: Failed with status {response.status}")
            print(await response.text())

        # Test 7: List tasks again to see completion
        print("\n7. Listing tasks after completion attempt...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   TASKS: {result['response']}")
            else:
                print(f"   ERROR: Unexpected response format: {result}")
        else:
            print(f"   ERROR: Failed with status {response.status}")
            print(await response.text())

        # Test 8: Try to delete task by number
        print("\n8. Trying to delete task 1...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Delete task 1"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   RESPONSE: {result['response']}")
                if "deleted" in result['response']:
                    print("   SUCCESS: Task deletion by number working!")
                else:
                    print("   ISSUE: Task deletion by number not working")
            else:
                print(f"   ERROR: Unexpected response format: {result}")
        else:
            print(f"   ERROR: Failed with status {response.status}")
            print(await response.text())

        # Test 9: Show completed tasks
        print("\n9. Trying to show completed tasks...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show completed tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   RESPONSE: {result['response']}")
            else:
                print(f"   ERROR: Unexpected response format: {result}")
        else:
            print(f"   ERROR: Failed with status {response.status}")
            print(await response.text())

        print("\n=== Specific feature tests completed ===")

if __name__ == "__main__":
    asyncio.run(test_specific_features())