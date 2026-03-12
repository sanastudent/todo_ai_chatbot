#!/usr/bin/env python3
"""
Simple test to check if the database and basic functionality work.
"""
import asyncio
import json
import sys
import os

# Add the backend src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

# Import using the backend path structure
from backend.src.models.task import Task
from backend.src.services.database import async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from uuid import uuid4
from datetime import datetime

async def test_raw_database():
    """Test raw database operations"""
    print("Testing raw database operations...")

    try:
        # Test database connection by creating a session
        async with AsyncSession(async_engine) as session:
            print("[SUCCESS] Database session created successfully")

            # Test a simple query to see if tables exist
            result = await session.exec(select(Task).limit(1))
            tasks = result.all()
            print(f"[SUCCESS] Query executed successfully, found {len(tasks)} existing tasks")

            # Try to insert a new task directly
            new_task = Task(
                id=str(uuid4()),
                user_id="test_user_123",
                title="Test task for debugging",
                description="This is a test task created to debug the database issue",
                completed=False,
                priority="medium",
                tags=json.dumps(["test", "debug"]),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(new_task)
            await session.commit()
            print(f"[SUCCESS] Direct database insertion succeeded, task ID: {new_task.id}")

            # Verify the task was created
            retrieved_task = await session.get(Task, new_task.id)
            if retrieved_task:
                print(f"[SUCCESS] Task verification successful: {retrieved_task.title}")
            else:
                print("[ERROR] Could not retrieve the created task")

            return True

    except Exception as e:
        print(f"[ERROR] Database operation failed: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

async def main():
    print("[INFO] Starting raw database test...")
    success = await test_raw_database()

    if success:
        print("\n[SUCCESS] Database connection and operations work correctly!")
        print("The issue is likely in the MCP tools layer or AI agent, not the database.")
    else:
        print("\n[ERROR] Database connection failed - this is the root cause.")

if __name__ == "__main__":
    asyncio.run(main())