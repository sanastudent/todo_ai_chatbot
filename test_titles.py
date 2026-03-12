import asyncio
import aiohttp
import json

async def test_task_titles():
    """Test to see what titles are actually being stored"""
    user_id = "test-user-titles"

    async with aiohttp.ClientSession() as session:
        # Add task 1
        print("Adding first task...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Add task to buy groceries"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"Response: {result['response']}")
        else:
            print(f"Failed: {response.status}")
            print(await response.text())

        # Add task 2 with slight variation
        print("\nAdding second task with same content...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Add task to buy groceries"},  # Same content
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"Response: {result['response']}")
        else:
            print(f"Failed: {response.status}")
            print(await response.text())

        # Check tasks with list all
        print("\nListing all tasks...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"All tasks: {result['response']}")
        else:
            print(f"Failed: {response.status}")
            print(await response.text())

        # Try to add task with different phrasing
        print("\nAdding task with different phrasing...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "buy groceries"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"Response: {result['response']}")
        else:
            print(f"Failed: {response.status}")
            print(await response.text())

        # Check tasks again
        print("\nListing all tasks after third add...")
        response = await session.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"All tasks: {result['response']}")
        else:
            print(f"Failed: {response.status}")
            print(await response.text())

if __name__ == "__main__":
    asyncio.run(test_task_titles())