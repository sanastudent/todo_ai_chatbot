#!/usr/bin/env python3
"""
Analysis script to test the current state of the task manager system
and identify why the intermediate features are failing.
"""

import sys
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock

# Add the backend/src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_src_dir = os.path.join(current_dir, 'backend', 'src')
sys.path.insert(0, backend_src_dir)

from services.agent import (
    extract_search_term,
    extract_tags_filter,
    extract_priority_filter,
    extract_sort_params,
    extract_task_details_for_update,
    extract_task_title_to_complete,
    extract_task_title_to_delete,
    find_matching_tasks,
    enhanced_mock_response
)


async def test_search_functionality():
    """Test the search functionality that appears to be broken."""
    print("🔍 Testing SEARCH functionality...")

    # Test cases that should work according to the requirements
    test_cases = [
        ("find milk", "milk"),
        ("look for fruits", "fruits"),
        ("search book", "book"),
        ("find report", "report"),
        ("find tasks with milk", "milk"),
        ('find milk"', 'milk'),  # Test with trailing quotes
        ('"find milk"', 'milk'),  # Test with surrounding quotes
    ]

    for input_msg, expected in test_cases:
        result = extract_search_term(input_msg.lower())
        print(f"  Input: '{input_msg}' → Output: '{result}' (Expected: '{expected}')")
        if result != expected and not (result is None and expected is None):
            print(f"    ❌ FAILED - Expected '{expected}', got '{result}'")
        else:
            print(f"    ✅ PASSED")


async def test_tag_functionality():
    """Test the tag functionality that appears to be broken."""
    print("\n🏷️  Testing TAG functionality...")

    # Test cases for tag extraction
    tag_test_cases = [
        ("show urgent tasks", ["urgent"]),
        ("show tasks tagged important", ["important"]),
        ("show work tasks", ["work"]),
        ("filter by tag work", ["work"]),
        ("filter by tag work and priority high", ["work"]),
        ("find work items", ["work"]),  # This should return None as it's tag-based
    ]

    for input_msg, expected in tag_test_cases:
        result = extract_tags_filter(input_msg.lower())
        print(f"  Input: '{input_msg}' → Output: {result} (Expected: {expected})")
        if result != expected and not (result is None and expected is None):
            print(f"    ❌ FAILED - Expected {expected}, got {result}")
        else:
            print(f"    ✅ PASSED")

    # Test "add tag" functionality
    print("\n  Testing 'add tag' command parsing:")
    update_test_cases = [
        ("add important tag to task 1", ("1_add_tag_important", None, None)),
        ("add tag urgent to task 2", ("2_add_tag_urgent", None, None)),
        ("remove work tag from task 3", ("3_remove_tag_work", None, None)),
    ]

    for input_msg, expected in update_test_cases:
        result = extract_task_details_for_update(input_msg)
        print(f"  Input: '{input_msg}' → Output: {result} (Expected: {expected})")
        if result != expected:
            print(f"    ❌ FAILED - Expected {expected}, got {result}")
        else:
            print(f"    ✅ PASSED")


async def test_priority_help():
    """Test the priority color help functionality."""
    print("\n🔴 Testing PRIORITY COLOR HELP functionality...")

    # Mock objects for the enhanced_mock_response function
    mock_user_id = "test_user"
    mock_db_session = AsyncMock()

    help_queries = [
        "show me priority colors meaning",
        "show me priority color meaning",
        "priority colors meaning",
        "priority color",
        "colors meaning"
    ]

    for query in help_queries:
        print(f"  Testing: '{query}'")
        response = await enhanced_mock_response(query, mock_user_id, mock_db_session)
        if "🔴" in response and "High Priority" in response:
            print(f"    ✅ PASSED - Contains priority color info")
        else:
            print(f"    ❌ FAILED - Does not contain priority color info")
            print(f"      Response: {response}")


async def test_filter_functionality():
    """Test the filtering functionality."""
    print("\n📊 Testing FILTER functionality...")

    # Test priority filtering
    priority_test_cases = [
        ("show high priority work", ["high"]),
        ("show medium shopping tasks", ["medium"]),
        ("filter work and high", ["high"]),  # This might not work as expected
        ("filter by tag work and priority high", ["high"]),
    ]

    for input_msg, expected in priority_test_cases:
        result = extract_priority_filter(input_msg.lower())
        print(f"  Input: '{input_msg}' → Priority Output: {result} (Expected: {expected})")
        if result != expected and not (result is None and expected is None):
            print(f"    ❌ FAILED - Expected {expected}, got {result}")
        else:
            print(f"    ✅ PASSED")


async def test_task_management():
    """Test task management commands."""
    print("\n📝 Testing TASK MANAGEMENT functionality...")

    # Test complete task extraction
    complete_test_cases = [
        ("complete task 1", "1"),
        ("finish task 2", "2"),
        ("complete buy groceries", "buy groceries"),
    ]

    for input_msg, expected in complete_test_cases:
        result = extract_task_title_to_complete(input_msg)
        print(f"  Complete - Input: '{input_msg}' → Output: '{result}' (Expected: '{expected}')")
        if result != expected and not (result is None and expected is None):
            print(f"    ❌ FAILED - Expected '{expected}', got '{result}'")
        else:
            print(f"    ✅ PASSED")

    # Test delete task extraction
    delete_test_cases = [
        ("delete task 1", "1"),
        ("remove task 2", "2"),
        ("delete buy groceries", "buy groceries"),
    ]

    for input_msg, expected in delete_test_cases:
        result = extract_task_title_to_delete(input_msg)
        print(f"  Delete - Input: '{input_msg}' → Output: '{result}' (Expected: '{expected}')")
        if result != expected and not (result is None and expected is None):
            print(f"    ❌ FAILED - Expected '{expected}', got '{result}'")
        else:
            print(f"    ✅ PASSED")


async def test_sort_functionality():
    """Test the sorting functionality."""
    print("\n🔄 Testing SORT functionality...")

    sort_test_cases = [
        ("show newest high priority tasks", {"sort_by": "created_at", "sort_order": "desc"}),
        ("sort by newest", {"sort_by": "created_at", "sort_order": "desc"}),
        ("show oldest tasks", {"sort_by": "created_at", "sort_order": "asc"}),
    ]

    for input_msg, expected in sort_test_cases:
        result = extract_sort_params(input_msg.lower())
        print(f"  Input: '{input_msg}' → Output: {result} (Expected: {expected})")
        # Check if expected keys are in result
        success = True
        for key, value in expected.items():
            if result.get(key) != value:
                success = False
                break

        if success:
            print(f"    ✅ PASSED")
        else:
            print(f"    ❌ FAILED - Expected {expected}, got {result}")


async def run_analysis():
    """Run all tests to analyze the system."""
    print("🔍 ANALYZING TODO AI CHATBOT SYSTEM")
    print("=" * 50)

    await test_search_functionality()
    await test_tag_functionality()
    await test_priority_help()
    await test_filter_functionality()
    await test_task_management()
    await test_sort_functionality()

    print("\n" + "=" * 50)
    print("📊 ANALYSIS COMPLETE")
    print("\nBased on this analysis, we can identify which features are working vs failing.")


if __name__ == "__main__":
    asyncio.run(run_analysis())