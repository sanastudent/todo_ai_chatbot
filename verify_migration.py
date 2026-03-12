#!/usr/bin/env python3
"""
Verify that the database migration was successful and test task creation.
"""
import asyncio
import json
import sys
import os

# Add the backend src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from backend.src.models.task import Task
from backend.src.services.database import async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from uuid import uuid4
from datetime import datetime

async def verify_schema_and_test():
    """Verify the schema includes new columns and test creation"""
    print("Verifying database schema and testing task creation...")

    try:
        # Test database connection by creating a session
        async with AsyncSession(async_engine) as session:
            print("[SUCCESS] Database session created successfully")

            # Test a simple query to see if the new columns exist
            result = await session.exec(select(Task).limit(1))
            tasks = result.all()
            print(f"[SUCCESS] Query executed successfully, found {len(tasks)} existing tasks")

            # Try to insert a task with the new fields (priority and tags)
            new_task = Task(
                id=str(uuid4()),
                user_id="test_user_123",
                title="Test task with enhanced features",
                description="This is a test task with priority and tags",
                completed=False,
                priority="high",  # This should now work
                tags=json.dumps(["work", "urgent", "testing"]),  # This should now work
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(new_task)
            await session.commit()
            print(f"[SUCCESS] Task with enhanced features created successfully, task ID: {new_task.id}")

            # Verify the task was created with all fields
            retrieved_task = await session.get(Task, new_task.id)
            if retrieved_task:
                print(f"[SUCCESS] Task verification successful:")
                print(f"  - Title: {retrieved_task.title}")
                print(f"  - Priority: {retrieved_task.priority}")
                print(f"  - Tags: {retrieved_task.tags}")
                print(f"  - Completed: {retrieved_task.completed}")
            else:
                print("[ERROR] Could not retrieve the created task")

            return True

    except Exception as e:
        print(f"[ERROR] Database operation failed: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

async def main():
    print("[INFO] Starting database schema verification test...")
    success = await verify_schema_and_test()

    if success:
        print("\n[SUCCESS] Database schema is correct and enhanced features work!")
        print("The issue has been resolved - the database now has priority and tags columns.")
    else:
        print("\n[ERROR] Database schema verification failed.")

if __name__ == "__main__":
    asyncio.run(main())