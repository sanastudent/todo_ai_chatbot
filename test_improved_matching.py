import asyncio
import aiohttp
import json

async def test_improved_matching():
    """Test the improved agent matching logic"""
    print("=== Testing Improved Matching Logic ===\n")

    BASE_URL = "http://localhost:8002"

    async with aiohttp.ClientSession() as session:
        user_id = "improved-matching-test"

        # Test 1: Add some tasks
        print("1. Adding tasks...")
        tasks_to_add = [
            "buy groceries",
            "walk the dog",
            "call mom",
            "finish report"
        ]

        for task in tasks_to_add:
            response = await session.post(
                f"{BASE_URL}/api/{user_id}/chat",
                json={"message": f"Add task to {task}"},
                headers={"Content-Type": "application/json"}
            )

            if response.status == 200:
                result = await response.json()
                if 'response' in result:
                    print(f"   Added: {task}")
                else:
                    print(f"   Error adding {task}: {result}")
            else:
                print(f"   Error adding {task}: {response.status}")

        # Test 2: List all tasks
        print("\n2. Listing all tasks...")
        response = await session.post(
            f"{BASE_URL}/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            response_text = result['response']
            # Replace Unicode characters that cause encoding issues
            safe_response = response_text.encode('ascii', 'replace').decode('ascii')
            print(f"   Response: {safe_response}")
        else:
            print(f"   Error: {response.status}")

        # Test 3: Test numbered task completion
        print("\n3. Testing numbered task completion...")
        response = await session.post(
            f"{BASE_URL}/api/{user_id}/chat",
            json={"message": "Complete task 1"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            response_text = result['response']
            # Replace Unicode characters that cause encoding issues
            safe_response = response_text.encode('ascii', 'replace').decode('ascii')
            print(f"   Response: {safe_response}")
        else:
            print(f"   Error: {response.status}")

        # Test 4: Test partial title matching (should match "buy groceries" with "groceries")
        print("\n4. Testing partial title matching...")
        response = await session.post(
            f"{BASE_URL}/api/{user_id}/chat",
            json={"message": "Complete task groceries"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            response_text = result['response']
            # Replace Unicode characters that cause encoding issues
            safe_response = response_text.encode('ascii', 'replace').decode('ascii')
            print(f"   Response: {safe_response}")
        else:
            print(f"   Error: {response.status}")

        # Test 5: Test "Finish the groceries task" pattern
        print("\n5. Testing 'Finish the X task' pattern...")
        # First add the task back
        response = await session.post(
            f"{BASE_URL}/api/{user_id}/chat",
            json={"message": "Add task to buy groceries"},
            headers={"Content-Type": "application/json"}
        )

        response = await session.post(
            f"{BASE_URL}/api/{user_id}/chat",
            json={"message": "Finish the groceries task"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            response_text = result['response']
            # Replace Unicode characters that cause encoding issues
            safe_response = response_text.encode('ascii', 'replace').decode('ascii')
            print(f"   Response: {safe_response}")
        else:
            print(f"   Error: {response.status}")

        # Test 6: Test delete by number
        print("\n6. Testing delete by number...")
        response = await session.post(
            f"{BASE_URL}/api/{user_id}/chat",
            json={"message": "Delete task 2"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            response_text = result['response']
            # Replace Unicode characters that cause encoding issues
            safe_response = response_text.encode('ascii', 'replace').decode('ascii')
            print(f"   Response: {safe_response}")
        else:
            print(f"   Error: {response.status}")

        # Test 7: Test delete by partial title
        print("\n7. Testing delete by partial title...")
        # First add the task back
        response = await session.post(
            f"{BASE_URL}/api/{user_id}/chat",
            json={"message": "Add task to walk the dog"},
            headers={"Content-Type": "application/json"}
        )

        response = await session.post(
            f"{BASE_URL}/api/{user_id}/chat",
            json={"message": "Delete task dog"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            response_text = result['response']
            # Replace Unicode characters that cause encoding issues
            safe_response = response_text.encode('ascii', 'replace').decode('ascii')
            print(f"   Response: {safe_response}")
        else:
            print(f"   Error: {response.status}")

        # Test 8: Test "list all tasks" command
        print("\n8. Testing 'list all tasks' command...")
        response = await session.post(
            f"{BASE_URL}/api/{user_id}/chat",
            json={"message": "List all tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            response_text = result['response']
            # Replace Unicode characters that cause encoding issues
            safe_response = response_text.encode('ascii', 'replace').decode('ascii')
            print(f"   Response: {safe_response}")
        else:
            print(f"   Error: {response.status}")

        print("\n=== Testing Complete ===")

if __name__ == "__main__":
    asyncio.run(test_improved_matching())