#!/usr/bin/env python3
"""
Debug script to test the specific "add groceries" scenario that causes HTTP 500 errors
"""
import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock

# Add backend/src to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from src.services.agent import invoke_agent, extract_task_title
from src.mcp.tools import add_task
from sqlmodel.ext.asyncio.session import AsyncSession


async def test_add_groceries_scenario():
    """Test the specific scenario that was causing HTTP 500 errors"""
    print("Testing 'add groceries' scenario...")

    # Test the extract_task_title function first
    test_message = "add groceries"
    extracted_title = extract_task_title(test_message)
    print(f"Extracted title from '{test_message}': '{extracted_title}'")

    # Create a mock database session
    mock_session = MagicMock(spec=AsyncSession)
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Simulate what happens in the invoke_agent function when processing "add groceries"
    user_message_lower = "add groceries"
    user_id = "test_user_123"

    # Check if this matches the add task condition
    add_phrases = [
        "add task", "add a task", "create task", "create a task",
        "new task", "remember to", "need to", "have to", "should"
    ]

    matches_add = any(phrase in user_message_lower for phrase in add_phrases)
    print(f"Does '{user_message_lower}' match add phrases? {matches_add}")

    if matches_add:
        title = extract_task_title("add groceries")
        print(f"Extracted title: '{title}'")

        if title:
            print(f"Title is valid: '{title}'")
            # In a real scenario, this would call add_task, but we'll just verify the logic path
        else:
            print("Title extraction failed - this could cause issues")

    print("Test completed - no immediate issues found in basic logic")


async def test_edge_cases():
    """Test various edge cases that might cause HTTP 500 errors"""
    print("\nTesting edge cases...")

    test_cases = [
        "",  # Empty message
        "   ",  # Whitespace only
        "add",  # Very short message
        "add ",  # Add with space
        "add groceries",  # Normal case
        "ADD GROCERIES",  # Uppercase
        "Add Groceries",  # Capitalized
    ]

    for case in test_cases:
        try:
            extracted = extract_task_title(case)
            print(f"'{case}' -> '{extracted}'")
        except Exception as e:
            print(f"ERROR with '{case}': {e}")

    print("Edge case testing completed")


if __name__ == "__main__":
    print("Starting HTTP 500 debug tests...")
    asyncio.run(test_add_groceries_scenario())
    asyncio.run(test_edge_cases())
    print("\nDebug tests completed.")