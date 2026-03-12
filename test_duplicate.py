import asyncio
import aiohttp
import json

async def test_duplicate_prevention():
    """Test duplicate task prevention specifically"""
    user_id = "test-user-duplicate"

    async with aiohttp.ClientSession() as session:
        # Add a task for the first time
        print("Adding task for the first time...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Add task to buy groceries"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"First add response: {result['response']}")
        else:
            print(f"First add failed: {response.status}")
            print(await response.text())
            return

        # Try to add the same task again
        print("\nTrying to add the same task again (should be prevented)...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Add task to buy groceries"},  # Same task
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"Second add response: {result['response']}")
        else:
            print(f"Second add failed: {response.status}")
            print(await response.text())
            return

        # List tasks to see if there's only one
        print("\nListing tasks to verify there's only one...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"List tasks response: {result['response']}")
        else:
            print(f"List tasks failed: {response.status}")
            print(await response.text())

if __name__ == "__main__":
    asyncio.run(test_duplicate_prevention())