import asyncio
import aiohttp
import json

async def debug_test():
    """Debug test to check both commands work properly"""
    base_url = "http://localhost:8000"

    async with aiohttp.ClientSession() as session:
        user_id = "test-user-debug"

        print("=== Testing 'add tag urgent to task 1' ===")
        try:
            response = await session.post(
                f"{base_url}/api/{user_id}/chat",
                json={"message": "add tag urgent to task 1"},
                headers={"Content-Type": "application/json"}
            )
            result = await response.json()
            print(f"SUCCESS: {result['response']}")
        except Exception as e:
            print(f"ERROR: {e}")

        print("\n=== Testing 'show high priority tasks' ===")
        try:
            response = await session.post(
                f"{base_url}/api/{user_id}/chat",
                json={"message": "show high priority tasks"},
                headers={"Content-Type": "application/json"}
            )
            result = await response.json()
            # Handle potential encoding issues when printing
            try:
                print(f"SUCCESS: {result['response']}")
            except UnicodeEncodeError:
                print(f"SUCCESS (with encoding): Response received but contains special characters")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(debug_test())