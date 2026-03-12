import asyncio
import aiohttp
import json

async def test_numbered_tasks():
    """Test numbered task functionality"""
    user_id = "test-user-numbered"

    async with aiohttp.ClientSession() as session:
        # Add a first task
        print("Adding first task...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Add task to buy groceries"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"First task response: {result['response']}")
        else:
            print(f"First task failed: {response.status}")
            print(await response.text())

        # Add a second task
        print("\nAdding second task...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Add task to walk the dog"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"Second task response: {result['response']}")
        else:
            print(f"Second task failed: {response.status}")
            print(await response.text())

        # List tasks to see the numbering
        print("\nListing tasks to see numbering...")
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

        # Try to complete task #1 (buy groceries)
        print("\nTrying to complete task 1...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Complete task 1"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"Complete task 1 response: {result['response']}")
        else:
            print(f"Complete task 1 failed: {response.status}")
            print(await response.text())

        # List tasks again to see completion
        print("\nListing tasks again to see completion...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"List tasks after completion: {result['response']}")
        else:
            print(f"List tasks after completion failed: {response.status}")
            print(await response.text())

if __name__ == "__main__":
    asyncio.run(test_numbered_tasks())