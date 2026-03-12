import asyncio
import httpx
import json

async def test_enhanced_features():
    """Test that the backend supports enhanced features (priority, tags, search, filter, sort)"""

    base_url = "http://localhost:8000"

    # Test 1: Send a message to add a task with priority and tags
    async with httpx.AsyncClient(timeout=30.0) as client:
        # First, add a high priority task with tags
        response = await client.post(
            f"{base_url}/api/testuser/chat",
            json={
                "message": "Add a task to buy groceries with high priority and tags work and urgent"
            }
        )

        print(f"Add task response: {response.status_code}")
        print(f"Response content: {response.text}")

        if response.status_code == 200:
            result = response.json()
            print(f"Task added successfully: {result}")

            # Now try to list tasks to see if our enhanced features are working
            response = await client.post(
                f"{base_url}/api/testuser/chat",
                json={
                    "message": "Show me my tasks",
                    "conversation_id": result.get("conversation_id")
                }
            )

            print(f"List tasks response: {response.status_code}")
            print(f"Response content: {response.text}")
        else:
            print("Failed to add task")

        # Test the health endpoint as well
        health_response = await client.get(f"{base_url}/health")
        print(f"Health check: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"Health details: {health_response.json()}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_features())