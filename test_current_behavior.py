#!/usr/bin/env python3
"""
Test the current behavior of the agent to identify the issues
"""
import sys
import os

# Add backend src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from backend.src.services.agent import (
    extract_tags_filter,
    extract_search_term
)


def test_current_behavior():
    """Test current behavior of the parsing functions"""
    print("Testing current behavior of agent parsing functions...")
    print("=" * 60)

    # Test cases that should work but might not
    test_cases = [
        ("Show work tasks", "extract_tags_filter", extract_tags_filter),
        ("Find shopping items", "extract_search_term", extract_search_term),
        ("Filter by tag shopping", "extract_tags_filter", extract_tags_filter),
        ("Show tasks with work tag", "extract_tags_filter", extract_tags_filter),
        ("Show shopping tasks", "extract_tags_filter", extract_tags_filter),
    ]

    for command, func_name, func in test_cases:
        result = func(command.lower())
        print(f"'{command}' -> {func_name}: {result}")

    print("=" * 60)


def test_list_task_triggers():
    """Test what triggers the list tasks functionality"""
    message = "Show work tasks"
    message_lower = message.lower()

    # Current list task trigger phrases
    trigger_phrases = [
        "show my tasks", "show tasks", "list tasks", "what tasks", "my tasks",
        "show pending", "show my pending", "pending tasks", "list pending",
        "what do i need to do", "todo list", "to do list", "what's on my list",
        "list all tasks", "show completed tasks", "show all tasks", "list all",
        "filter by", "search for", "sort tasks", "sort by", "find tasks"
    ]

    print("\nChecking if 'Show work tasks' triggers list tasks:")
    for phrase in trigger_phrases:
        if phrase in message_lower:
            print(f"  YES '{phrase}' found in '{message}'")
        else:
            print(f"  NO '{phrase}' not found in '{message}'")

    # Check if any of the phrases match
    matches_any = any(phrase in message_lower for phrase in trigger_phrases)
    print(f"\nOverall match: {'YES' if matches_any else 'NO'}")


def main():
    print("ANALYZING CURRENT AGENT BEHAVIOR")
    print("Identifying why certain commands are not recognized...")
    print()

    test_current_behavior()
    test_list_task_triggers()

    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY:")
    print("1. 'Show work tasks' - May not trigger list_tasks due to missing pattern")
    print("2. 'Find shopping items' - Should trigger via 'find tasks' pattern")
    print("3. 'Filter by tag shopping' - May not match current tag patterns")
    print("=" * 60)


if __name__ == "__main__":
    main()