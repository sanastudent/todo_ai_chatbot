#!/usr/bin/env python3
"""
Final test script to verify that all intermediate features work properly
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
    extract_sort_params,
)


def test_command_parsing():
    """Test that the command parsing functions work correctly"""
    print("Testing command parsing functions...")

    # Test 1: "Add high priority task"
    print("\n1. Testing 'Add high priority task'")
    title, priority, tags = extract_task_details_with_priority_and_tags("Add high priority task")
    print(f"   Title: '{title}', Priority: '{priority}', Tags: {tags}")
    assert title == "task" and priority == "high", f"Expected title='task', priority='high', got title='{title}', priority='{priority}'"

    # Test 2: "Add work task"
    print("\n2. Testing 'Add work task'")
    title, priority, tags = extract_task_details_with_priority_and_tags("Add work task")
    print(f"   Title: '{title}', Priority: '{priority}', Tags: {tags}")
    assert title == "task" and "work" in (tags or []), f"Expected title='task', tags contain 'work', got title='{title}', tags={tags}"

    # Test 3: "Filter by priority high"
    print("\n3. Testing 'Filter by priority high'")
    priority_filter = extract_priority_filter("filter by priority high")
    print(f"   Priority filter: {priority_filter}")
    assert priority_filter == ["high"], f"Expected ['high'], got {priority_filter}"

    # Test 4: "Search for grocery tasks"
    print("\n4. Testing 'Search for grocery tasks'")
    search_term = extract_search_term("search for grocery tasks")
    print(f"   Search term: '{search_term}'")
    assert search_term == "grocery", f"Expected 'grocery', got '{search_term}'"

    # Test 5: "Sort tasks by date"
    print("\n5. Testing 'Sort tasks by date'")
    sort_params = extract_sort_params("sort tasks by date")
    print(f"   Sort params: {sort_params}")
    assert sort_params.get('sort_by') == 'created_at', f"Expected sort_by='created_at', got {sort_params.get('sort_by')}"

    # Test 6: "Add tag shopping"
    print("\n6. Testing 'Add tag shopping'")
    title, priority, tags = extract_task_details_with_priority_and_tags("Add tag shopping")
    print(f"   Title: '{title}', Priority: '{priority}', Tags: {tags}")
    assert title == "shopping" and "shopping" in (tags or []), f"Expected title='shopping' and tags contain 'shopping', got title='{title}', tags={tags}"

    print("\nAll command parsing tests passed!")


def test_additional_cases():
    """Test additional cases to ensure robustness"""
    print("\nTesting additional command cases...")

    # Test "Add a high priority task to buy groceries"
    print("\n1. Testing 'Add a high priority task to buy groceries'")
    title, priority, tags = extract_task_details_with_priority_and_tags("Add a high priority task to buy groceries")
    print(f"   Title: '{title}', Priority: '{priority}', Tags: {tags}")
    assert "buy groceries" in title and priority == "high", f"Expected 'buy groceries' in title and priority='high', got title='{title}', priority='{priority}'"

    # Test "Create task with tags work and urgent"
    print("\n2. Testing 'Create task with tags work and urgent'")
    title, priority, tags = extract_task_details_with_priority_and_tags("Create task with tags work and urgent")
    print(f"   Title: '{title}', Priority: '{priority}', Tags: {tags}")
    assert "work" in (tags or []) and "urgent" in (tags or []), f"Expected tags to contain 'work' and 'urgent', got tags={tags}"

    # Test "Show tasks with high priority"
    print("\n3. Testing 'Show tasks with high priority'")
    priority_filter = extract_priority_filter("show tasks with high priority")
    print(f"   Priority filter: {priority_filter}")
    assert priority_filter == ["high"], f"Expected ['high'], got {priority_filter}"

    # Test "List tasks tagged with work"
    print("\n4. Testing 'List tasks tagged with work'")
    tags_filter = extract_tags_filter("list tasks tagged with work")
    print(f"   Tags filter: {tags_filter}")
    assert tags_filter == ["work"], f"Expected ['work'], got {tags_filter}"

    # Test "Sort tasks by priority"
    print("\n5. Testing 'Sort tasks by priority'")
    sort_params = extract_sort_params("sort tasks by priority")
    print(f"   Sort params: {sort_params}")
    assert sort_params.get('sort_by') == 'priority', f"Expected sort_by='priority', got {sort_params.get('sort_by')}"

    print("\nAll additional command tests passed!")


def main():
    print("Testing Todo AI Chatbot Intermediate Features")
    print("=" * 50)

    try:
        test_command_parsing()
        test_additional_cases()

        print("\n" + "=" * 50)
        print("ALL TESTS PASSED! The intermediate features are working correctly.")
        print("=" * 50)

        # Show a summary of what was tested
        print("\nSUMMARY OF TESTED FEATURES:")
        print("- Add high priority task: Parsed correctly")
        print("- Add work task: Parsed correctly")
        print("- Filter by priority high: Parsed correctly")
        print("- Search for grocery tasks: Parsed correctly")
        print("- Sort tasks by date: Parsed correctly")
        print("- Add tag shopping: Parsed correctly")

    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()