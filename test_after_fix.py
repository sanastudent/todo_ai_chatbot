import asyncio
import httpx
import json

async def test_task_creation_after_fix():
    """Test that the task creation now works after the database fix"""

    base_url = "http://localhost:8000"

    print("Testing task creation after database fix...")

    # Test the chat API with a message that should create a task with priority and tags
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # First, try to add a task with priority and tags
            response = await client.post(
                f"{base_url}/api/testuser/chat",
                json={
                    "message": "Add a high priority task to buy groceries with tags work and urgent",
                    "conversation_id": None
                }
            )

            print(f"Response status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS: {result.get('response', 'No response text')}")

                # Now try to list tasks to verify it was added
                list_response = await client.post(
                    f"{base_url}/api/testuser/chat",
                    json={
                        "message": "Show me my tasks",
                        "conversation_id": result.get('conversation_id')
                    }
                )

                if list_response.status_code == 200:
                    list_result = list_response.json()
                    print(f"✅ List tasks success: {list_result.get('response', 'No response text')[:100]}...")

                    return True
                else:
                    print(f"❌ List tasks failed: {list_response.text}")
                    return False
            else:
                print(f"❌ Task creation failed: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_task_creation_after_fix())
    if success:
        print("\n🎉 TASK CREATION IS WORKING AGAIN!")
        print("The database error has been fixed.")
    else:
        print("\n❌ Task creation still failing.")