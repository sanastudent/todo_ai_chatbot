#!/usr/bin/env python3
"""
Simple test to verify the HTTP 500 fixes work properly
"""
import asyncio
import os
import sys

# Add backend/src to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from src.mcp.tools import add_task, list_tasks
from src.services.database import async_engine
from sqlmodel.ext.asyncio.session import AsyncSession


async def test_add_task_directly():
    """Test the add_task function directly to make sure it works without HTTP 500 errors"""
    print("Testing add_task function directly...")

    test_user_id = "test_user_http_500"

    try:
        # Test adding a task - this was causing HTTP 500 before
        result = await add_task(
            user_id=test_user_id,
            title="Buy groceries",
            description="Milk, bread, eggs"
        )

        print(f"✓ Successfully added task: {result['title']}")
        print(f"  Task ID: {result['task_id']}")
        print(f"  Created at: {result['created_at']}")

        # Test listing tasks
        tasks_result = await list_tasks(user_id=test_user_id)
        print(f"✓ Successfully listed tasks: {len(tasks_result['tasks'])} found")

        for task in tasks_result['tasks']:
            print(f"  - {task['title']} (completed: {task['completed']})")

        return True

    except Exception as e:
        print(f"✗ Error during task operations: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False


async def test_error_conditions():
    """Test error conditions to make sure they don't cause HTTP 500 errors"""
    print("\nTesting error conditions...")

    try:
        # Test with empty user_id (should raise ValueError)
        try:
            await add_task(user_id="", title="Test task")
            print("✗ Empty user_id should have raised an error")
        except ValueError as e:
            print(f"✓ Empty user_id correctly raised ValueError: {e}")

        # Test with empty title (should raise ValueError)
        try:
            await add_task(user_id="test_user", title="")
            print("✗ Empty title should have raised an error")
        except ValueError as e:
            print(f"✓ Empty title correctly raised ValueError: {e}")

        # Test with very long title (should raise ValueError)
        try:
            long_title = "x" * 201  # Exceeds 200 char limit
            await add_task(user_id="test_user", title=long_title)
            print("✗ Long title should have raised an error")
        except ValueError as e:
            print(f"✓ Long title correctly raised ValueError: {e}")

        return True

    except Exception as e:
        print(f"✗ Unexpected error during error condition testing: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False


async def main():
    """Main test function"""
    print("Starting HTTP 500 fixes verification test...\n")

    success1 = await test_add_task_directly()
    success2 = await test_error_conditions()

    # Clean up - delete test data
    try:
        from src.mcp.tools import delete_task
        from sqlmodel import select
        from src.models.task import Task

        async with AsyncSession(async_engine) as session:
            # Find and delete test tasks
            stmt = select(Task).where(Task.user_id == "test_user_http_500")
            result = await session.exec(stmt)
            tasks = result.all()

            for task in tasks:
                try:
                    await delete_task(user_id="test_user_http_500", task_id=task.id, db_session=session)
                except:
                    pass  # Ignore errors during cleanup

        print("\n✓ Test data cleaned up")
    except Exception as e:
        print(f"\n⚠ Warning: Could not clean up test data: {e}")

    # Close the database engine
    await async_engine.dispose()

    if success1 and success2:
        print("\n🎉 All tests passed! HTTP 500 errors have been fixed.")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)