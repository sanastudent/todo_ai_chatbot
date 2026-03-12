#!/usr/bin/env python3
"""
Test the main features that were requested
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


def test_main_requirements():
    """Test the main requirements from the original problem"""
    print("Testing main requirements...")

    # 1. "Add high priority task" not recognized
    print("\n1. Testing 'Add high priority task'")
    title, priority, tags = extract_task_details_with_priority_and_tags("Add high priority task")
    print(f"   Result -> Title: '{title}', Priority: '{priority}', Tags: {tags}")
    success1 = title == "task" and priority == "high"
    print(f"   {'PASS' if success1 else 'FAIL'}: Title='task', Priority='high'")

    # 2. "Add work task" not recognized
    print("\n2. Testing 'Add work task'")
    title, priority, tags = extract_task_details_with_priority_and_tags("Add work task")
    print(f"   Result -> Title: '{title}', Priority: '{priority}', Tags: {tags}")
    success2 = title == "task" and "work" in (tags or [])
    print(f"   {'PASS' if success2 else 'FAIL'}: Title='task', Tags contain 'work'")

    # 3. "Filter by priority high" not working
    print("\n3. Testing 'Filter by priority high'")
    priority_filter = extract_priority_filter("filter by priority high")
    print(f"   Result -> Priority filter: {priority_filter}")
    success3 = priority_filter == ["high"]
    print(f"   {'PASS' if success3 else 'FAIL'}: Priority filter=['high']")

    # 4. "Search for grocery tasks" not working
    print("\n4. Testing 'Search for grocery tasks'")
    search_term = extract_search_term("search for grocery tasks")
    print(f"   Result -> Search term: '{search_term}'")
    success4 = search_term == "grocery"
    print(f"   {'PASS' if success4 else 'FAIL'}: Search term='grocery'")

    # 5. "Sort tasks by date" not working
    print("\n5. Testing 'Sort tasks by date'")
    sort_params = extract_sort_params("sort tasks by date")
    print(f"   Result -> Sort params: {sort_params}")
    success5 = sort_params.get('sort_by') == 'created_at'
    print(f"   {'PASS' if success5 else 'FAIL'}: Sort by='created_at'")

    # 6. "Add tag shopping" not recognized
    print("\n6. Testing 'Add tag shopping'")
    title, priority, tags = extract_task_details_with_priority_and_tags("Add tag shopping")
    print(f"   Result -> Title: '{title}', Priority: '{priority}', Tags: {tags}")
    success6 = title == "shopping" and "shopping" in (tags or [])
    print(f"   {'PASS' if success6 else 'FAIL'}: Title='shopping', Tags contain 'shopping'")

    all_success = all([success1, success2, success3, success4, success5, success6])

    print(f"\n{'ALL MAIN FEATURES WORKING!' if all_success else 'SOME FEATURES NEED FIXING'}")
    return all_success


def main():
    print("Testing Todo AI Chatbot Main Requirements")
    print("=" * 50)

    success = test_main_requirements()

    if success:
        print("\n" + "=" * 50)
        print("ALL MAIN INTERMEDIATE FEATURES ARE WORKING!")
        print("=" * 50)
        print("\nFeatures implemented:")
        print("- Add high priority task: Parsed with priority")
        print("- Add work task: Parsed with work as tag")
        print("- Filter by priority high: Parsed as priority filter")
        print("- Search for grocery tasks: Parsed as search term")
        print("- Sort tasks by date: Parsed as sort parameter")
        print("- Add tag shopping: Parsed with shopping as tag")
        print("\nThe AI agent can now properly understand and handle")
        print("all the requested intermediate features!")
    else:
        print("\nSome features still need work")
        sys.exit(1)


if __name__ == "__main__":
    main()