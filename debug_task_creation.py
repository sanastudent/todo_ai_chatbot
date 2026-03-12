#!/usr/bin/env python3
"""
Debug script to test the task creation functionality and identify the database error.
"""
import asyncio
import json
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import sys
import os

# Add the backend src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend/src'))

from mcp.tools import add_task
from services.database import async_engine
from models.task import Task

async def test_direct_task_creation():
    """Test task creation directly using the add_task function"""
    print("Testing direct task creation...")

    try:
        # Test with minimal parameters
        result = await add_task(
            user_id="test_user",
            title="Test task from debug script",
            description="This is a test task created for debugging purposes"
        )
        print(f"✅ Direct task creation succeeded: {result}")
        return True
    except Exception as e:
        print(f"❌ Direct task creation failed: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

async def test_task_creation_with_priority_and_tags():
    """Test task creation with enhanced features (priority and tags)"""
    print("\nTesting task creation with priority and tags...")

    try:
        # Test with priority and tags
        result = await add_task(
            user_id="test_user",
            title="Test task with priority and tags",
            description="Task with enhanced features for testing",
            priority="high",
            tags=["work", "urgent", "testing"]
        )
        print(f"✅ Enhanced task creation succeeded: {result}")
        return True
    except Exception as e:
        print(f"❌ Enhanced task creation failed: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

async def test_database_connection():
    """Test raw database connection"""
    print("\nTesting raw database connection...")

    try:
        async with AsyncSession(async_engine) as session:
            # Test a simple query
            result = await session.exec(select(Task).limit(1))
            tasks = result.all()
            print(f"✅ Database connection works, found {len(tasks)} existing tasks")

            # Try to create a task directly using SQLModel
            from uuid import uuid4
            from datetime import datetime

            new_task = Task(
                id=str(uuid4()),
                user_id="test_user",
                title="Direct DB test task",
                description="Created directly via database session",
                completed=False,
                priority="medium",
                tags=json.dumps(["test", "direct"]),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(new_task)
            await session.commit()
            print(f"✅ Direct database insertion succeeded, task ID: {new_task.id}")

            return True
    except Exception as e:
        print(f"❌ Database connection test failed: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

async def main():
    print("🔍 Starting debug of task creation issue...")

    # Test 1: Raw database connection
    db_ok = await test_database_connection()

    if db_ok:
        # Test 2: Direct function call
        direct_ok = await test_direct_task_creation()

        if direct_ok:
            # Test 3: Enhanced features
            enhanced_ok = await test_task_creation_with_priority_and_tags()

            if enhanced_ok:
                print("\n✅ All tests passed! The issue might be in the AI agent parsing, not the database layer.")
            else:
                print("\n⚠️  Enhanced features test failed, but basic functionality works.")
        else:
            print("\n❌ Basic task creation failed - the issue is in the add_task function.")
    else:
        print("\n❌ Database connection failed - the issue is at the database level.")

if __name__ == "__main__":
    asyncio.run(main())