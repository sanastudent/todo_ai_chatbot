import asyncio
import aiohttp
import json

async def test_all_features():
    """Comprehensive test of all MCP tools functionality"""
    user_id = "test-user-comprehensive"

    print("=== Starting Comprehensive Feature Test ===\n")

    async with aiohttp.ClientSession() as session:
        # Test 1: Add task (should work and prevent duplicates)
        print("1. Testing ADD TASK functionality...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Add task to buy groceries"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   [SUCCESS] Add task response: {result['response']}")
            else:
                print(f"   ✗ Add task unexpected response format: {result}")
        else:
            print(f"   ✗ Add task failed: {response.status}")
            print(await response.text())

        # Test duplicate prevention
        print("\n2. Testing DUPLICATE PREVENTION...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Add task to buy groceries"},  # Same task
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   ✓ Duplicate prevention response: {result['response']}")
            else:
                print(f"   ✗ Duplicate prevention unexpected response format: {result}")
        else:
            print(f"   ✗ Duplicate test failed: {response.status}")
            print(await response.text())

        # Test 3: List tasks
        print("\n3. Testing LIST TASKS functionality...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   ✓ List tasks response: {result['response']}")
            else:
                print(f"   ✗ List tasks unexpected response format: {result}")
        else:
            print(f"   ✗ List tasks failed: {response.status}")
            print(await response.text())

        # Test 4: Add another task
        print("\n4. Testing ADD ANOTHER TASK...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Add task to walk the dog"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   ✓ Add second task response: {result['response']}")
            else:
                print(f"   ✗ Add second task unexpected response format: {result}")
        else:
            print(f"   ✗ Add second task failed: {response.status}")
            print(await response.text())

        # Test 5: List tasks again to see both
        print("\n5. Testing LIST TASKS with multiple tasks...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   ✓ Multiple tasks response: {result['response']}")
            else:
                print(f"   ✗ Multiple tasks response unexpected format: {result}")
        else:
            print(f"   ✗ Multiple tasks list failed: {response.status}")
            print(await response.text())

        # Test 6: Complete task by number
        print("\n6. Testing COMPLETE TASK BY NUMBER...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Complete task 1"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   ✓ Complete task by number response: {result['response']}")
            else:
                print(f"   ✗ Complete task by number unexpected response format: {result}")
        else:
            print(f"   ✗ Complete task by number failed: {response.status}")
            print(await response.text())

        # Test 7: List tasks to see completion status
        print("\n7. Testing LIST TASKS to verify completion...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   ✓ Tasks after completion: {result['response']}")
            else:
                print(f"   ✗ Tasks after completion unexpected response format: {result}")
        else:
            print(f"   ✗ List after completion failed: {response.status}")
            print(await response.text())

        # Test 8: Show completed tasks only
        print("\n8. Testing LIST COMPLETED TASKS...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show completed tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   ✓ Completed tasks response: {result['response']}")
            else:
                print(f"   ✗ Completed tasks response unexpected format: {result}")
        else:
            print(f"   ✗ Completed tasks list failed: {response.status}")
            print(await response.text())

        # Test 9: Show pending tasks only
        print("\n9. Testing LIST PENDING TASKS...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show pending tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   ✓ Pending tasks response: {result['response']}")
            else:
                print(f"   ✗ Pending tasks response unexpected format: {result}")
        else:
            print(f"   ✗ Pending tasks list failed: {response.status}")
            print(await response.text())

        # Test 10: Delete task
        print("\n10. Testing DELETE TASK...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Delete task 1"},  # Should delete the completed task
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   ✓ Delete task response: {result['response']}")
            else:
                print(f"   ✗ Delete task response unexpected format: {result}")
        else:
            print(f"   ✗ Delete task failed: {response.status}")
            print(await response.text())

        # Test 11: Final list to verify deletion
        print("\n11. Testing FINAL LIST after deletion...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            if 'response' in result:
                print(f"   ✓ Final tasks list: {result['response']}")
            else:
                print(f"   ✗ Final tasks list unexpected response format: {result}")
        else:
            print(f"   ✗ Final list failed: {response.status}")
            print(await response.text())

        print("\n=== All tests completed ===")

if __name__ == "__main__":
    asyncio.run(test_all_features())