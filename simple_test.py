#!/usr/bin/env python3
"""
Simple test to verify the fixes work properly
"""
import asyncio
import os
import sys

# Add backend/src to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from src.mcp.tools import add_task, list_tasks, complete_task, update_task, delete_task
from src.services.database import async_engine
from sqlmodel.ext.asyncio.session import AsyncSession


async def test_basic_functionality():
    """Test basic functionality of MCP tools"""
    print("Testing basic functionality...")

    test_user_id = "test_user_simple"

    # Test 1: Add a task
    print("\n1. Testing add_task...")
    try:
        result = await add_task(
            user_id=test_user_id,
            title="Test task for verification",
            description="This is a simple test task"
        )
        print(f"   ✓ Successfully added task: {result['title']}")
        task_id = result['task_id']
    except Exception as e:
        print(f"   ✗ Failed to add task: {e}")
        return False

    # Test 2: List tasks
    print("\n2. Testing list_tasks...")
    try:
        result = await list_tasks(user_id=test_user_id)
        print(f"   ✓ Successfully listed tasks: {len(result['tasks'])} found")
        for task in result['tasks']:
            print(f"     - {task['title']}")
    except Exception as e:
        print(f"   ✗ Failed to list tasks: {e}")
        return False

    # Test 3: Complete task
    print("\n3. Testing complete_task...")
    try:
        result = await complete_task(
            user_id=test_user_id,
            task_id=task_id
        )
        print(f"   ✓ Successfully completed task: {result}")
    except Exception as e:
        print(f"   ✗ Failed to complete task: {e}")
        return False

    # Test 4: Update task
    print("\n4. Testing update_task...")
    try:
        result = await update_task(
            user_id=test_user_id,
            task_id=task_id,
            title="Updated test task"
        )
        print(f"   ✓ Successfully updated task: {result}")
    except Exception as e:
        print(f"   ✗ Failed to update task: {e}")
        return False

    # Test 5: Delete task
    print("\n5. Testing delete_task...")
    try:
        result = await delete_task(
            user_id=test_user_id,
            task_id=task_id
        )
        print(f"   ✓ Successfully deleted task: {result}")
    except Exception as e:
        print(f"   ✗ Failed to delete task: {e}")
        return False

    print("\n✓ All basic functionality tests passed!")
    return True


async def main():
    """Main test function"""
    print("Starting basic functionality test...")

    success = await test_basic_functionality()

    # Close the database engine
    await async_engine.dispose()

    if success:
        print("\n🎉 All tests passed! The fixes are working properly.")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)