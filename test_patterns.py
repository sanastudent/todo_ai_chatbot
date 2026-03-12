#!/usr/bin/env python3
"""
Test script to validate that the natural language patterns are correctly implemented
"""

import re

def test_patterns():
    print("Testing natural language patterns for MCP tools...")

    # Define the patterns as implemented in agent.py
    patterns = {
        'filter_tasks': [
            r'tasks with (.+?) tag',
            r'filter tasks by (.+?) category',
            r'show me (.+?) priority tasks',
            r'pending (.+?) tasks',
            r'filter by (.+?) priority and (.+?) category'
        ],

        'add_task_with_details': [
            r'add (.+?) task to (.+?) with (.+?) tag',
            r'create (.+?) priority (.+?) task: (.+?) by (.+?)',
            r'add (.+?) task: (.+?) with (.+?) tag',
            r'create task: (.+?) with (.+?) tag'
        ],

        'get_task_stats': [
            r"what(\'s| is) my completion rate",
            r'show (?:my |task )?statistics',
            r'task summary for (.+?)',
            r'how many tasks (?:did I |have I )(complete|completed) (.+)',
            r'show priority distribution'
        ],

        'bulk_operations': [
            r'complete all (.+?) tasks',
            r'mark all (.+?) tasks as (.+?) priority',
            r'delete all (.+?) tasks',
            r'add (.+?) tag to all (.+?) tasks',
            r'uncomplete task (\d+) and (\d+)'
        ]
    }

    # Test cases
    test_messages = [
        ("tasks with urgent tag", "filter_tasks"),
        ("filter tasks by work category", "filter_tasks"),
        ("show me high priority tasks", "filter_tasks"),
        ("pending work tasks", "filter_tasks"),
        ("filter by high priority and work category", "filter_tasks"),
        ("add high task to buy groceries with shopping tag", "add_task_with_details"),
        ("create high priority work task: prepare presentation by tomorrow", "add_task_with_details"),
        ("add medium task: call dentist with appointment tag", "add_task_with_details"),
        ("create task: buy milk with grocery tag", "add_task_with_details"),
        ("what's my completion rate", "get_task_stats"),
        ("show my statistics", "get_task_stats"),
        ("task summary for this week", "get_task_stats"),
        ("how many tasks did I complete this week", "get_task_stats"),
        ("how many tasks have I completed this month", "get_task_stats"),
        ("show priority distribution", "get_task_stats"),
        ("complete all shopping tasks", "bulk_operations"),
        ("mark all work tasks as high priority", "bulk_operations"),
        ("delete all personal tasks", "bulk_operations"),
        ("add urgent tag to all work tasks", "bulk_operations"),
        ("uncomplete task 1 and 2", "bulk_operations")
    ]

    print("\nPattern Matching Tests:")
    print("=" * 50)

    all_passed = True

    for message, expected_tool in test_messages:
        matched = False
        for tool, tool_patterns in patterns.items():
            for pattern in tool_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    if tool == expected_tool:
                        print(f"PASS: '{message}' -> {tool} (CORRECT)")
                    else:
                        print(f"FAIL: '{message}' -> {tool} (WRONG, expected {expected_tool})")
                        all_passed = False
                    matched = True
                    break
            if matched:
                break

        if not matched:
            print(f"FAIL: '{message}' -> NO MATCH (expected {expected_tool})")
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("ALL TESTS PASSED! Patterns are correctly implemented.")
    else:
        print("SOME TESTS FAILED! There are issues with pattern matching.")

    return all_passed

if __name__ == "__main__":
    test_patterns()