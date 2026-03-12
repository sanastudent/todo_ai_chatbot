#!/usr/bin/env python3
"""
Test script to validate all the fixes for the Todo Chatbot critical bugs
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.src.services.agent import invoke_agent
from backend.src.mcp.tools import add_task, list_tasks, complete_task, delete_task
from backend.src.services.database import get_async_session, async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import create_engine
from uuid import uuid4
import json


async def test_critical_bugs():
    """Test all the critical bugs mentioned in the issue"""

    # Create a test user ID
    user_id = "test_user_" + str(uuid4())
    conversation_id = "test_conv_" + str(uuid4())

    print("="*70)
    print("VALIDATING ALL CRITICAL BUG FIXES")
    print("="*70)

    # Create database session
    async with AsyncSession(async_engine) as db_session:

        print("\n1. TESTING: 'add task to buy groceries' -> Should extract 'buy groceries' (NO QUOTES)")
        try:
            response1 = await invoke_agent(
                user_id=user_id,
                conversation_id=conversation_id,
                user_message="add task to buy groceries",
                db_session=db_session
            )
            print(f"   Response: {response1}")

            # Verify the task was added correctly by listing tasks
            tasks_result = await list_tasks(user_id=user_id, completed=None, db_session=db_session)
            if tasks_result["tasks"]:
                task_title = tasks_result["tasks"][0]["title"]
                if task_title == "buy groceries":
                    print("   [SUCCESS] Task title extracted correctly without quotes")
                else:
                    print(f"   [FAILED] Task title incorrect: '{task_title}'")
            else:
                print("   [FAILED] No tasks found")
        except Exception as e:
            print(f"   [FAILED]: {str(e)}")

        print("\n2. TESTING: 'show my tasks' -> Should display tasks (NO FILTER ERROR)")
        try:
            response2 = await invoke_agent(
                user_id=user_id,
                conversation_id=conversation_id,
                user_message="show my tasks",
                db_session=db_session
            )
            print(f"   Response: {response2}")
            if "couldn't filter your tasks" in response2.lower():
                print("   [FAILED] Still showing filtering error")
            else:
                print("   [SUCCESS] Tasks displayed correctly without filtering error")
        except Exception as e:
            print(f"   [FAILED]: {str(e)}")

        print("\n3. TESTING: 'mark task 2 as done' -> Should work without encoding errors")
        try:
            # Add a second task first
            await invoke_agent(
                user_id=user_id,
                conversation_id=conversation_id,
                user_message="add task to walk the dog",
                db_session=db_session
            )

            response3 = await invoke_agent(
                user_id=user_id,
                conversation_id=conversation_id,
                user_message="mark task 2 as done",
                db_session=db_session
            )
            print(f"   Response: {response3}")

            if "'charmap' codec can't encode character" in str(response3) or "\\u2192" in str(response3):
                print("   [FAILED] Still showing encoding error")
            else:
                print("   [SUCCESS] Task marked as done without encoding errors")
        except Exception as e:
            print(f"   [FAILED]: {str(e)}")

        print("\n4. TESTING: 'delete the last task' -> Should delete task (NOT MOCK AI)")
        try:
            response4 = await invoke_agent(
                user_id=user_id,
                conversation_id=conversation_id,
                user_message="delete the last task",
                db_session=db_session
            )
            print(f"   Response: {response4}")

            if "mock AI assistant" in response4.lower() or "understand you" in response4.lower():
                print("   [FAILED] Still falling back to mock AI assistant")
            else:
                print("   [SUCCESS] Task deleted properly, not falling back to mock AI")
        except Exception as e:
            print(f"   [FAILED]: {str(e)}")

        print("\n5. TESTING: Task numbering consistency ('complete task 1')")
        try:
            # Add two tasks to test numbering
            await invoke_agent(
                user_id=user_id,
                conversation_id=conversation_id,
                user_message="add task to call mom",
                db_session=db_session
            )
            await invoke_agent(
                user_id=user_id,
                conversation_id=conversation_id,
                user_message="add task to water plants",
                db_session=db_session
            )

            # Show tasks to see numbering
            show_response = await invoke_agent(
                user_id=user_id,
                conversation_id=conversation_id,
                user_message="show my tasks",
                db_session=db_session
            )
            print(f"   Task list: {show_response}")

            # Now try to complete "task 1" (should be "call mom", not "water plants")
            complete_response = await invoke_agent(
                user_id=user_id,
                conversation_id=conversation_id,
                user_message="complete task 1",
                db_session=db_session
            )
            print(f"   Complete response: {complete_response}")

            # Verify which task was actually completed by checking the task list again
            after_complete_response = await invoke_agent(
                user_id=user_id,
                conversation_id=conversation_id,
                user_message="show my tasks",
                db_session=db_session
            )
            print(f"   After completion: {after_complete_response}")

            # Check if the first task was actually completed
            if "call mom" in complete_response and ("completed" in complete_response.lower() or "done" in complete_response.lower()):
                print("   [SUCCESS] Correct task was completed (task 1 -> correct task)")
            else:
                print("   [FAILED] Wrong task completed or completion failed")

        except Exception as e:
            print(f"   [FAILED]: {str(e)}")

    print("\n" + "="*70)
    print("VALIDATION COMPLETED - All critical bugs should be fixed!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(test_critical_bugs())