#!/usr/bin/env python3
"""
Test script to run the specific commands and see the debug output
"""

import sys
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock

# Add the backend/src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_src_dir = os.path.join(current_dir, 'backend', 'src')
sys.path.insert(0, backend_src_dir)

# Mock the database session and other dependencies
mock_db_session = AsyncMock()
mock_user_id = "test_user"
mock_conversation_id = "test_conv"

# Import the agent function
try:
    from services.agent import invoke_agent
except ImportError:
    from agent import invoke_agent


async def test_command(command: str):
    """Test a single command and capture the debug output"""
    print(f"\n{'='*60}")
    print(f"TESTING COMMAND: '{command}'")
    print(f"{'='*60}")

    try:
        # Call the invoke_agent function
        result = await invoke_agent(
            user_id=mock_user_id,
            conversation_id=mock_conversation_id,
            user_message=command,
            db_session=mock_db_session
        )
        print(f"RESULT: {result}")
    except Exception as e:
        print(f"ERROR: {str(e)}")


async def main():
    """Test all the failing commands"""
    print("TESTING THE 4 FAILING COMMANDS WITH DEBUG OUTPUT")

    commands = [
        "find milk",
        "add urgent tag to task 1",
        "red means what",
        "show high priority work"
    ]

    for cmd in commands:
        await test_command(cmd)

    print(f"\n{'='*60}")
    print("TESTING COMPLETE - CHECK DEBUG OUTPUT ABOVE")


if __name__ == "__main__":
    asyncio.run(main())