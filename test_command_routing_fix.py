"""
Test script to validate command routing fixes
Tests that previously failing commands now work via regex patterns
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from src.services.agent import invoke_agent
from src.database import async_engine
from sqlmodel.ext.asyncio.session import AsyncSession


async def test_command_routing():
    """Test all command variations that were previously failing"""

    test_user_id = "test-user-routing"
    test_conversation_id = "test-conv-routing"

    # Create a database session
    async with AsyncSession(async_engine) as session:

        print("=" * 80)
        print("TESTING COMMAND ROUTING FIXES")
        print("=" * 80)

        # Test cases that were previously failing
        test_cases = [
            # List/Show commands (previously failed)
            ("show my tasks", "Should list all tasks"),
            ("list my tasks", "Should list all tasks"),
            ("show tasks", "Should list all tasks"),
            ("list tasks", "Should list all tasks"),

            # Complete commands with variations (previously failed)
            ("complete my task 1", "Should complete task 1"),
            ("complete task 1 please", "Should complete task 1"),
            ("finish my task 1", "Should complete task 1"),
            ("mark my task 1 done", "Should complete task 1"),
            ("mark task 1 as done", "Should complete task 1"),

            # Delete commands with variations (previously failed)
            ("delete my task 3", "Should delete task 3"),
            ("delete task 3 please", "Should delete task 3"),
            ("remove my task 2", "Should delete task 2"),
            ("cancel my task 1", "Should delete task 1"),

            # Commands that were already working (should still work)
            ("add buy fruits", "Should add task"),
            ("update task 1 to go for dinner", "Should update task 1"),
            ("complete task 1", "Should complete task 1"),
            ("delete task 1", "Should delete task 1"),
        ]

        print("\nTesting command patterns:\n")

        for command, expected_behavior in test_cases:
            print(f"\n{'─' * 80}")
            print(f"Command: '{command}'")
            print(f"Expected: {expected_behavior}")
            print(f"{'─' * 80}")

            try:
                response = await invoke_agent(
                    user_id=test_user_id,
                    conversation_id=test_conversation_id,
                    user_message=command,
                    db_session=session
                )

                # Check if response contains mock AI fallback message
                is_mock_response = "I understand you said" in response or "As a mock AI assistant" in response
                is_api_unavailable = "⚠️ Note: AI natural language processing is not available" in response

                if is_mock_response or is_api_unavailable:
                    print(f"❌ FAILED - Got mock/fallback response:")
                    print(f"   {response[:200]}...")
                else:
                    print(f"✅ SUCCESS - Got real response:")
                    print(f"   {response[:200]}")

            except Exception as e:
                print(f"❌ ERROR: {str(e)}")

        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print("\nIf you see '✅ SUCCESS' for all commands, the routing fix is working!")
        print("If you see '❌ FAILED' with mock responses, the patterns may need adjustment.")
        print("\nNote: Some commands may fail if tasks don't exist (e.g., 'complete task 1')")
        print("      This is expected behavior - the important thing is that they don't")
        print("      fall back to mock AI responses.")
        print("=" * 80)


async def test_pattern_matching():
    """Test regex pattern matching directly"""
    import re

    print("\n" + "=" * 80)
    print("TESTING REGEX PATTERN MATCHING")
    print("=" * 80)

    # Test patterns
    patterns = [
        (r'^(?:show|list)(?: my)? tasks[.!?]*\s*$', [
            "show tasks",
            "list tasks",
            "show my tasks",
            "list my tasks"
        ]),
        (r'^complete(?: my)? task (\d+)(?: please)?[.!?]*\s*$', [
            "complete task 1",
            "complete my task 1",
            "complete task 1 please",
            "complete my task 2 please"
        ]),
        (r'^delete(?: my)? task (\d+)(?: please)?[.!?]*\s*$', [
            "delete task 3",
            "delete my task 3",
            "delete task 3 please",
            "delete my task 1 please"
        ]),
    ]

    for pattern, test_strings in patterns:
        print(f"\nPattern: {pattern}")
        print("─" * 80)
        for test_str in test_strings:
            match = re.search(pattern, test_str.lower())
            if match:
                print(f"  ✅ '{test_str}' → MATCH")
                if match.groups():
                    print(f"     Groups: {match.groups()}")
            else:
                print(f"  ❌ '{test_str}' → NO MATCH")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("\n🔍 Starting command routing validation tests...\n")

    # Run pattern matching tests first
    asyncio.run(test_pattern_matching())

    # Then run full integration tests
    asyncio.run(test_command_routing())

    print("\n✅ Test script completed!\n")
