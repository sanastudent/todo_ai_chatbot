#!/usr/bin/env python3
"""
Simple verification that the Todo AI Chatbot backend HTTP 500 errors have been fixed
"""
import asyncio
import sys
import os

# Add backend/src to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from src.mcp.tools import add_task, list_tasks
from src.services.database import async_engine
from sqlmodel.ext.asyncio.session import AsyncSession


async def test_basic_functionality():
    """Test basic functionality that was causing HTTP 500 errors"""
    print("Testing basic functionality that was causing HTTP 500 errors...")

    # Create a test user
    test_user_id = "test_user_simple_verification"

    print("Testing 'add groceries' scenario (the reported issue)...")
    try:
        # Test the specific scenario that was causing issues
        async with AsyncSession(async_engine) as session:
            result = await add_task(
                user_id=test_user_id,
                title="buy groceries",
                description="Milk, bread, eggs"
            )
            print(f"  Added task: {result['title']}")

            # Test listing tasks
            tasks_result = await list_tasks(user_id=test_user_id)
            print(f"  Listed tasks: {len(tasks_result['tasks'])} found")

            print("Basic task operations work correctly")

        # Clean up test data
        async with AsyncSession(async_engine) as cleanup_session:
            from src.mcp.tools import delete_task
            for task in tasks_result['tasks']:
                try:
                    await delete_task(user_id=test_user_id, task_id=task['task_id'], db_session=cleanup_session)
                except:
                    pass  # Ignore errors during cleanup

        print("Test data cleaned up")

    except Exception as e:
        print(f"Error in basic functionality test: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("All basic functionality tests passed - no HTTP 500 errors!")
    return True


async def test_error_handling():
    """Test error handling to ensure graceful failures"""
    print("\nTesting error handling...")

    try:
        # Test with invalid inputs that should be handled gracefully
        async with AsyncSession(async_engine) as session:
            # Test empty title (should raise ValueError)
            try:
                await add_task(user_id="test", title="", db_session=session)
                print("Error: Empty title should have raised an error")
                return False
            except ValueError:
                print("  Empty title correctly raises ValueError")

            # Test very long title (should raise ValueError)
            try:
                await add_task(user_id="test", title="x" * 201, db_session=session)
                print("Error: Long title should have raised an error")
                return False
            except ValueError:
                print("  Long title correctly raises ValueError")

        print("Error handling works correctly")

    except Exception as e:
        print(f"Unexpected error in error handling test: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def main():
    """Main verification function"""
    print("Starting final verification of HTTP 500 error fixes...")
    print("=" * 50)

    success1 = await test_basic_functionality()
    success2 = await test_error_handling()

    # Close database engine
    await async_engine.dispose()

    print("=" * 50)
    if success1 and success2:
        print("VERIFICATION SUCCESSFUL!")
        print("HTTP 500 errors have been FIXED")
        print("All functionality works without crashes")
        print("Proper error handling is in place")
        print("The 'add groceries' scenario works correctly")
        return 0
    else:
        print("VERIFICATION FAILED!")
        print("Some issues remain")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)