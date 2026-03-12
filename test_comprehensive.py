import asyncio
import aiohttp
import json

async def test_backend_health():
    """Test if the backend is running and accessible"""
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get("http://localhost:8000/health")
            if response.status == 200:
                health_data = await response.json()
                print(f"[SUCCESS] Backend health check passed: {health_data}")
                return True
            else:
                print(f"[ERROR] Backend health check failed: {response.status}")
                return False
    except Exception as e:
        print(f"[ERROR] Could not connect to backend: {e}")
        return False

async def test_chatbot_comprehensive():
    """Test the chatbot functionality comprehensively"""
    # First check if backend is running
    if not await test_backend_health():
        print("[ERROR] Backend is not running. Please start the backend server first.")
        return

    async with aiohttp.ClientSession() as session:
        user_id = "test-user-comprehensive"

        print("\n=== TESTING ADD TASK ===")
        # Test adding a task
        response = await session.post(
            f"http://localhost:8000/api/{user_id}/chat",
            json={"message": "Add task to buy groceries"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"[SUCCESS] Add task response: {result['response']}")
        else:
            print(f"[ERROR] Add task failed: {response.status}")
            print(await response.text())

        print("\n=== TESTING ADD TASK WITH DESCRIPTION ===")
        # Test adding a task with description
        response = await session.post(
            f"http://localhost:8000/api/{user_id}/chat",
            json={"message": "Add task to walk the dog with description Take the golden retriever for a 30 minute walk"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"[SUCCESS] Add task with description response: {result['response']}")
        else:
            print(f"[ERROR] Add task with description failed: {response.status}")
            print(await response.text())

        print("\n=== TESTING LIST TASKS ===")
        # List tasks
        response = await session.post(
            f"http://localhost:8000/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"[SUCCESS] List tasks response: {result['response']}")
        else:
            print(f"[ERROR] List tasks failed: {response.status}")
            print(await response.text())

        print("\n=== TESTING COMPLETE TASK BY NUMBER ===")
        # Complete a task by number
        response = await session.post(
            f"http://localhost:8000/api/{user_id}/chat",
            json={"message": "Complete task 1"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"[SUCCESS] Complete task response: {result['response']}")
        else:
            print(f"[ERROR] Complete task failed: {response.status}")
            print(await response.text())

        print("\n=== TESTING LIST TASKS AGAIN TO SEE COMPLETION ===")
        # List tasks again to see completion
        response = await session.post(
            f"http://localhost:8000/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"[SUCCESS] List tasks response: {result['response']}")
        else:
            print(f"[ERROR] List tasks failed: {response.status}")
            print(await response.text())

        print("\n=== TESTING DUPLICATE PREVENTION ===")
        # Test duplicate prevention
        response = await session.post(
            f"http://localhost:8000/api/{user_id}/chat",
            json={"message": "Add task to buy groceries"},  # Same task as before
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"[SUCCESS] Duplicate task response: {result['response']}")
        else:
            print(f"[ERROR] Duplicate task test failed: {response.status}")
            print(await response.text())

        print("\n=== TESTING UPDATE TASK TITLE ===")
        # Test update task title
        response = await session.post(
            f"http://localhost:8000/api/{user_id}/chat",
            json={"message": 'Update "walk the dog" to "walk the golden retriever"'},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"[SUCCESS] Update task title response: {result['response']}")
        else:
            print(f"[ERROR] Update task title failed: {response.status}")
            print(await response.text())

        print("\n=== TESTING UPDATE TASK DESCRIPTION ===")
        # Test update task description
        response = await session.post(
            f"http://localhost:8000/api/{user_id}/chat",
            json={"message": 'Update "walk the golden retriever" description to Take the dog for a relaxing walk in the park'},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"[SUCCESS] Update task description response: {result['response']}")
        else:
            print(f"[ERROR] Update task description failed: {response.status}")
            print(await response.text())

        print("\n=== TESTING DELETE TASK ===")
        # Test delete task
        response = await session.post(
            f"http://localhost:8000/api/{user_id}/chat",
            json={"message": "Delete task 1"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"[SUCCESS] Delete task response: {result['response']}")
        else:
            print(f"[ERROR] Delete task failed: {response.status}")
            print(await response.text())

        print("\n=== TESTING LIST TASKS AFTER DELETION ===")
        # List tasks again after deletion
        response = await session.post(
            f"http://localhost:8000/api/{user_id}/chat",
            json={"message": "Show my tasks"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"[SUCCESS] Final list tasks response: {result['response']}")
        else:
            print(f"[ERROR] Final list tasks failed: {response.status}")
            print(await response.text())

        print("\n=== TESTING HELP COMMAND ===")
        # Test help command
        response = await session.post(
            f"http://localhost:8000/api/{user_id}/chat",
            json={"message": "Help"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"[SUCCESS] Help response: {result['response']}")
        else:
            print(f"[ERROR] Help command failed: {response.status}")
            print(await response.text())

        print("\n=== TESTING NATURAL LANGUAGE UNDERSTANDING ===")
        # Test natural language understanding
        response = await session.post(
            f"http://localhost:8000/api/{user_id}/chat",
            json={"message": "I need to remember to call mom tomorrow"},
            headers={"Content-Type": "application/json"}
        )

        if response.status == 200:
            result = await response.json()
            print(f"[SUCCESS] Natural language response: {result['response']}")
        else:
            print(f"[ERROR] Natural language command failed: {response.status}")
            print(await response.text())

if __name__ == "__main__":
    asyncio.run(test_chatbot_comprehensive())