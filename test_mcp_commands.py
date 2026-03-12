#!/usr/bin/env python3
"""
Test script to verify all 5 MCP commands work properly
"""
import asyncio
import os
import sys
from datetime import datetime
from uuid import uuid4

# Add backend/src to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from sqlmodel import create_engine, text
from sqlmodel.ext.asyncio.session import AsyncSession
from src.mcp.tools import add_task, list_tasks, complete_task, update_task, delete_task
from src.services.database import async_engine


async def test_all_commands():
    """Test all 5 MCP commands with a test user"""
    print("Testing all 5 MCP commands...")

    # Use a test user ID
    test_user_id = "test_user_12345"

    # Test 1: Add a task
    print("\n1. Testing ADD TASK command...")
    try:
        result = await add_task(
            user_id=test_user_id,
            title="Test task 1",
            description="This is a test task for verification"
        )
        print(f"   ✓ Added task: {result}")
        task_id_1 = result["task_id"]
    except Exception as e:
        print(f"   ✗ Failed to add task: {e}")
        return False

    # Test 2: Add another task
    print("\n2. Testing ADD TASK command (second task)...")
    try:
        result = await add_task(
            user_id=test_user_id,
            title="Test task 2",
            description="Second test task"
        )
        print(f"   ✓ Added task: {result}")
        task_id_2 = result["task_id"]
    except Exception as e:
        print(f"   ✗ Failed to add task: {e}")
        return False

    # Test 3: List tasks
    print("\n3. Testing LIST TASKS command...")
    try:
        result = await list_tasks(user_id=test_user_id)
        print(f"   ✓ Listed tasks: {len(result['tasks'])} tasks found")
        for task in result['tasks']:
            print(f"     - {task['title']} (completed: {task['completed']})")
    except Exception as e:
        print(f"   ✗ Failed to list tasks: {e}")
        return False

    # Test 4: Complete a task
    print("\n4. Testing COMPLETE TASK command...")
    try:
        result = await complete_task(
            user_id=test_user_id,
            task_id=task_id_1
        )
        print(f"   ✓ Completed task: {result}")
    except Exception as e:
        print(f"   ✗ Failed to complete task: {e}")
        return False

    # Verify completion by listing tasks again
    print("   Verifying completion...")
    try:
        result = await list_tasks(user_id=test_user_id)
        for task in result['tasks']:
            if task['task_id'] == task_id_1:
                print(f"     - Task {task['title']} is now completed: {task['completed']}")
    except Exception as e:
        print(f"   ✗ Failed to verify completion: {e}")
        return False

    # Test 5: Update a task
    print("\n5. Testing UPDATE TASK command...")
    try:
        result = await update_task(
            user_id=test_user_id,
            task_id=task_id_2,
            title="Updated test task 2",
            description="Updated description for test task"
        )
        print(f"   ✓ Updated task: {result}")
    except Exception as e:
        print(f"   ✗ Failed to update task: {e}")
        return False

    # Verify update by listing tasks again
    print("   Verifying update...")
    try:
        result = await list_tasks(user_id=test_user_id)
        for task in result['tasks']:
            if task['task_id'] == task_id_2:
                print(f"     - Updated task: {task['title']}")
    except Exception as e:
        print(f"   ✗ Failed to verify update: {e}")
        return False

    # Test 6: Delete a task
    print("\n6. Testing DELETE TASK command...")
    try:
        result = await delete_task(
            user_id=test_user_id,
            task_id=task_id_2
        )
        print(f"   ✓ Deleted task: {result}")
    except Exception as e:
        print(f"   ✗ Failed to delete task: {e}")
        return False

    # Verify deletion by listing tasks again
    print("   Verifying deletion...")
    try:
        result = await list_tasks(user_id=test_user_id)
        print(f"     - Remaining tasks: {len(result['tasks'])}")
        for task in result['tasks']:
            print(f"       - {task['title']}")
    except Exception as e:
        print(f"   ✗ Failed to verify deletion: {e}")
        return False

    print("\n✓ All 5 MCP commands tested successfully!")
    return True


async def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")
    try:
        # We'll use a direct SQL approach to clean up since we need to bypass
        # the normal user_id validation for cleanup
        async with AsyncSession(async_engine) as session:
            from sqlalchemy import text

            # Delete test user's tasks
            await session.exec(
                text("DELETE FROM task WHERE user_id = :user_id"),
                {"user_id": "test_user_12345"}
            )
            await session.commit()
            print("   ✓ Test data cleaned up")
    except Exception as e:
        print(f"   ⚠ Could not clean up test data: {e}")


async def main():
    """Main test function"""
    print("Starting MCP commands test...")

    success = await test_all_commands()

    await cleanup_test_data()

    if success:
        print("\n🎉 All tests passed! MCP commands are working properly.")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)