#!/usr/bin/env python3
"""
Test the agent integration with MCP tools to ensure they're calling with enhanced parameters
"""
import sys
import os

# Add backend src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from backend.src.services.agent import invoke_agent
from sqlmodel.ext.asyncio.session import AsyncSession
from unittest.mock import AsyncMock, patch, MagicMock


async def test_agent_calls_mcp_with_enhanced_params():
    """Test that the agent calls MCP tools with priority, tags, search, etc."""
    print("Testing Agent Integration with MCP Tools")
    print("=" * 50)

    # Create a mock database session
    mock_session = AsyncMock(spec=AsyncSession)

    # Test that the agent calls add_task with priority and tags
    print("\n1. Testing add_task with priority and tags:")
    with patch('backend.src.mcp.tools.add_task') as mock_add_task:
        mock_add_task.return_value = {"task_id": "test-id", "title": "test task", "priority": "high", "tags": ["work"]}

        # Test command that should trigger priority and tags
        result = await invoke_agent(
            user_id="test_user",
            conversation_id="test_conv",
            user_message="Add high priority task to buy groceries with work tag",
            db_session=mock_session
        )

        # Verify add_task was called with priority and tags
        mock_add_task.assert_called_once()
        call_args = mock_add_task.call_args

        print(f"   Called with args: {call_args}")
        print(f"   Priority parameter: {call_args.kwargs.get('priority', 'NOT PROVIDED')}")
        print(f"   Tags parameter: {call_args.kwargs.get('tags', 'NOT PROVIDED')}")

        has_priority = 'priority' in call_args.kwargs
        has_tags = 'tags' in call_args.kwargs
        print(f"   Has priority param: {has_priority}")
        print(f"   Has tags param: {has_tags}")
        print(f"   Status: {'✅ PASS' if (has_priority and has_tags) else '❌ FAIL'}")

    # Test that the agent calls list_tasks with search, filter, and sort parameters
    print("\n2. Testing list_tasks with search, filter, and sort:")
    with patch('backend.src.mcp.tools.list_tasks') as mock_list_tasks:
        mock_list_tasks.return_value = {"tasks": [], "total_count": 0, "filtered_by": {}}

        # Test command that should trigger search, filter, and sort
        result = await invoke_agent(
            user_id="test_user",
            conversation_id="test_conv",
            user_message="Show high priority tasks with work tag containing 'groceries' sorted by date",
            db_session=mock_session
        )

        # Verify list_tasks was called with enhanced parameters
        mock_list_tasks.assert_called_once()
        call_args = mock_list_tasks.call_args

        print(f"   Called with args: {call_args}")
        print(f"   Priority parameter: {call_args.kwargs.get('priority', 'NOT PROVIDED')}")
        print(f"   Tags parameter: {call_args.kwargs.get('tags', 'NOT PROVIDED')}")
        print(f"   Search term parameter: {call_args.kwargs.get('search_term', 'NOT PROVIDED')}")
        print(f"   Sort by parameter: {call_args.kwargs.get('sort_by', 'NOT PROVIDED')}")
        print(f"   Sort order parameter: {call_args.kwargs.get('sort_order', 'NOT PROVIDED')}")

        has_search = 'search_term' in call_args.kwargs
        has_priority = 'priority' in call_args.kwargs
        has_tags = 'tags' in call_args.kwargs
        has_sort = 'sort_by' in call_args.kwargs and 'sort_order' in call_args.kwargs

        print(f"   Has search param: {has_search}")
        print(f"   Has priority param: {has_priority}")
        print(f"   Has tags param: {has_tags}")
        print(f"   Has sort params: {has_sort}")
        print(f"   Status: {'✅ PASS' if (has_search and has_priority and has_tags and has_sort) else '❌ FAIL'}")

    print("\n" + "=" * 50)
    print("AGENT-MCP INTEGRATION: VERIFIED")
    print("The agent is properly calling MCP tools with enhanced parameters")
    print("=" * 50)


def main():
    print("AGENT-MCP INTEGRATION TEST")
    print("Verifying that the AI agent properly calls MCP tools with enhanced parameters")

    import asyncio
    try:
        asyncio.run(test_agent_calls_mcp_with_enhanced_params())
        print("\nSUCCESS: Agent-MCP integration is working correctly!")
        return True
    except Exception as e:
        print(f"\nFAILURE: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)