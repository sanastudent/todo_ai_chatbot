#!/usr/bin/env python3
"""
Test script to validate that the 5 requested commands work correctly
"""

def test_patterns():
    """Test the exact patterns the user requested"""
    test_messages = [
        "find report",
        "add tag to task 1",
        "show high priority",
        "red means what",
        "sort alphabetically"
    ]

    print("Testing the 5 requested commands:")
    print("=" * 50)

    for msg in test_messages:
        msg_lower = msg.strip('"\'').lower()
        print(f"Message: '{msg}' -> processed as: '{msg_lower}'")

        # FIRST: Check for help patterns about priority colors
        help_patterns = ['priority color', 'color mean', 'red means']
        has_help = any(pattern in msg_lower for pattern in help_patterns)
        print(f"  Help patterns ('priority color', 'color mean', 'red means'): {has_help}")

        # SECOND: Check for search patterns
        search_patterns = ['find ', 'search ', 'look for ']
        has_search = any(pattern in msg_lower for pattern in search_patterns)
        print(f"  Search patterns ('find ', 'search ', 'look for '): {has_search}")

        # THIRD: Check for tag patterns
        has_add_tag_and_task = 'add tag' in msg_lower and 'task' in msg_lower
        print(f"  Tag patterns ('add tag' + 'task'): {has_add_tag_and_task}")

        # FOURTH: Check for filter patterns
        has_show_or_filter = 'show ' in msg_lower or 'filter ' in msg_lower
        print(f"  Filter patterns ('show ' or 'filter '): {has_show_or_filter}")

        # FIFTH: Check for sort patterns
        has_sort = 'sort' in msg_lower
        print(f"  Sort patterns ('sort'): {has_sort}")

        # SIXTH: Check for task creation
        has_add = 'add' in msg_lower
        print(f"  Task creation ('add'): {has_add}")

        # Determine which pattern matches first according to the required order
        if has_help:
            result = "HELP (priority color explanation)"
        elif has_search:
            result = "SEARCH (find/report functionality)"
        elif has_add_tag_and_task:
            result = "TAG MANAGEMENT (add tag to task)"
        elif has_show_or_filter:
            result = "FILTER (show/filter functionality)"
        elif has_sort:
            result = "SORT (sorting functionality)"
        elif has_add:
            result = "TASK CREATION (add task)"
        else:
            result = "OTHER (no specific pattern matched)"

        print(f"  -> Final classification: {result}")
        print("-" * 40)

if __name__ == "__main__":
    test_patterns()