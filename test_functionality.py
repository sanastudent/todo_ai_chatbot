import asyncio
import aiohttp
import json

async def test_chat_endpoint():
    """Test the chat endpoint with various commands"""
    base_url = "http://localhost:8000"

    # Create a session to maintain conversation
    async with aiohttp.ClientSession() as session:
        user_id = "test-user-debug"

        print("=== Testing 'show high priority tasks' ===")
        try:
            response = await session.post(
                f"{base_url}/api/{user_id}/chat",
                json={"message": "show high priority tasks"},
                headers={"Content-Type": "application/json"}
            )
            result = await response.json()
            print(f"Response: {result}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n=== Testing 'add tag urgent to task 1' ===")
        try:
            response = await session.post(
                f"{base_url}/api/{user_id}/chat",
                json={"message": "add tag urgent to task 1"},
                headers={"Content-Type": "application/json"}
            )
            result = await response.json()
            print(f"Response: {result}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n=== Testing 'add high priority task to buy groceries' ===")
        try:
            response = await session.post(
                f"{base_url}/api/{user_id}/chat",
                json={"message": "add high priority task to buy groceries"},
                headers={"Content-Type": "application/json"}
            )
            result = await response.json()
            print(f"Response: {result}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n=== Testing 'show my tasks' ===")
        try:
            response = await session.post(
                f"{base_url}/api/{user_id}/chat",
                json={"message": "show my tasks"},
                headers={"Content-Type": "application/json"}
            )
            result = await response.json()
            print(f"Response: {result}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat_endpoint())
