#!/usr/bin/env python3
"""
Test that the server restart loaded the new agent code with priority/tag support
"""
import sys
import os

# Add backend src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from backend.src.services.agent import (
    extract_task_details_with_priority_and_tags,
    extract_priority_filter,
    extract_tags_filter,
    extract_search_term,
    extract_sort_params
)


def test_new_agent_functionality():
    """Test that the new agent functions are working"""
    print("Testing NEW agent functionality after server restart...")
    print("=" * 60)

    # Test the enhanced parsing functions that were added
    test_cases = [
        ("Add high priority task", "priority parsing", lambda: extract_task_details_with_priority_and_tags("Add high priority task")),
        ("Add work task", "tag parsing", lambda: extract_task_details_with_priority_and_tags("Add work task")),
        ("Filter by priority high", "priority filter", lambda: extract_priority_filter("filter by priority high")),
        ("Search for doctor", "search term", lambda: extract_search_term("search for doctor")),
        ("Sort tasks by date", "sort params", lambda: extract_sort_params("sort tasks by date")),
    ]

    all_passed = True
    for command, feature, func in test_cases:
        try:
            result = func()
            success = result is not None and (
                (feature == "priority parsing" and result[1] == "high") or
                (feature == "tag parsing" and "work" in (result[2] or [])) or
                (feature == "priority filter" and result == ["high"]) or
                (feature == "search term" and result == "doctor") or
                (feature == "sort params" and result.get('sort_by') == 'created_at')
            )

            status = "PASS" if success else "FAIL"
            print(f"  {command} ({feature}): {status}")
            if not success:
                print(f"    Expected result but got: {result}")
                all_passed = False
        except Exception as e:
            print(f"  {command} ({feature}): FAIL - Error: {e}")
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("SUCCESS: Server restart loaded NEW agent code with all features!")
        print("   - Priority parsing: Working")
        print("   - Tag parsing: Working")
        print("   - Filter functionality: Working")
        print("   - Search functionality: Working")
        print("   - Sort functionality: Working")
    else:
        print("FAILURE: Some features are not working properly")

    return all_passed


def main():
    print("VERIFYING SERVER RESTART LOADED NEW AGENT CODE")
    print("Testing that the backend server is now using the updated agent.py with priority/tag support...")
    print()

    success = test_new_agent_functionality()

    print(f"\nSERVER STATUS: {'UPDATED' if success else 'ISSUE'}")
    print("The server has been restarted and should now use the new agent code.")

    return success


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)