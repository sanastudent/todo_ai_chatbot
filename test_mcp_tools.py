import asyncio
import sys
import os

# Add the backend src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from sqlmodel.ext.asyncio.session import AsyncSession
from mcp.tools import add_task, list_tasks, complete_task, update_task, delete_task
from services.database import async_engine

async def test_mcp_tools():
    """Test all 5 MCP tools directly"""
    user_id = "test-user-mcp"

    print("=== TESTING MCP TOOLS DIRECTLY ===")

    # Test adding a task
    print("\n1. Testing add_task...")
    try:
        result = await add_task(user_id=user_id, title="Test task 1", description="Test description 1")
        task_id_1 = result["task_id"]
        print(f"   [SUCCESS] Added task: {result}")
    except Exception as e:
        print(f"   [ERROR] Failed to add task: {e}")
        return

    # Add another task
    try:
        result = await add_task(user_id=user_id, title="Test task 2", description="Test description 2")
        task_id_2 = result["task_id"]
        print(f"   [SUCCESS] Added task: {result}")
    except Exception as e:
        print(f"   [ERROR] Failed to add task: {e}")
        return

    # Test listing tasks
    print("\n2. Testing list_tasks...")
    try:
        result = await list_tasks(user_id=user_id)
        print(f"   [SUCCESS] Listed tasks: {result}")
    except Exception as e:
        print(f"   [ERROR] Failed to list tasks: {e}")
        return

    # Test completing a task
    print("\n3. Testing complete_task...")
    try:
        result = await complete_task(user_id=user_id, task_id=task_id_1)
        print(f"   [SUCCESS] Completed task: {result}")
    except Exception as e:
        print(f"   [ERROR] Failed to complete task: {e}")
        return

    # Test updating a task
    print("\n4. Testing update_task...")
    try:
        result = await update_task(user_id=user_id, task_id=task_id_2, title="Updated task 2", description="Updated description 2")
        print(f"   [SUCCESS] Updated task: {result}")
    except Exception as e:
        print(f"   [ERROR] Failed to update task: {e}")
        return

    # Test deleting a task
    print("\n5. Testing delete_task...")
    try:
        result = await delete_task(user_id=user_id, task_id=task_id_2)
        print(f"   [SUCCESS] Deleted task: {result}")
    except Exception as e:
        print(f"   [ERROR] Failed to delete task: {e}")
        return

    # Final list to verify changes
    print("\n6. Final task list...")
    try:
        result = await list_tasks(user_id=user_id)
        print(f"   [SUCCESS] Final task list: {result}")
    except Exception as e:
        print(f"   [ERROR] Failed to list tasks: {e}")
        return

    print("\n=== ALL MCP TOOLS TESTED SUCCESSFULLY ===")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())