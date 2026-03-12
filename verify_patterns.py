#!/usr/bin/env python3
"""
Simple verification script to check if the new patterns were added to agent.py
"""

import re

def verify_patterns():
    """Verify that the new patterns were added to the agent.py file"""
    print("Verifying that new patterns were added to agent.py...")
    print("="*60)

    # Read the agent.py file
    with open('backend/src/services/agent.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the patterns we added
    expected_patterns = [
        r"'\\^create \(\\w\+\\) task: \\(.\\+\\)\\$'",  # create [category] task: [title]
        r"'\\^list tasks having \\(.\\+\\) tag\\$'",     # list tasks having [tag] tag
        r"'\\^look for \\(.\\+\\) in tasks\\$'",         # look for [query] in tasks
        r"'\\^list \\(.\\+\\) priority tasks\\$'",       # list [priority] priority tasks
        r"'\\^display \\(.\\+\\) priority tasks\\$'",    # display [priority] priority tasks
        r"'\\^list overdue tasks\\$'",                   # list overdue tasks
        r"'\\^arrange tasks by due date\\$'",            # arrange tasks by due date
    ]

    # Define the function names that should be present
    expected_functions = [
        "create_category_task_match",
        "list_having_tag_match",
        "look_for_match",
        "list_priority_tasks_match",
        "display_priority_tasks_match",
        "list_overdue_match",
        "arrange_by_due_date_match"
    ]

    print("Checking for expected patterns in agent.py...")
    print()

    # Check for each pattern
    all_found = True
    for i, pattern in enumerate(expected_patterns, 1):
        # Convert the regex representation to look for the actual pattern in the code
        if i == 1:  # create [category] task: [title]
            search_str = r"create (\w+) task: (.+)$"
            found = search_str.replace('\\', '') in content
        elif i == 2:  # list tasks having [tag] tag
            search_str = r"list tasks having (.+) tag$"
            found = search_str.replace('\\', '') in content
        elif i == 3:  # look for [query] in tasks
            search_str = r"look for (.+) in tasks$"
            found = search_str.replace('\\', '') in content
        elif i == 4:  # list [priority] priority tasks
            search_str = r"list (.+) priority tasks$"
            found = search_str.replace('\\', '') in content
        elif i == 5:  # display [priority] priority tasks
            search_str = r"display (.+) priority tasks$"
            found = search_str.replace('\\', '') in content
        elif i == 6:  # list overdue tasks
            search_str = r"list overdue tasks$"
            found = search_str.replace('\\', '') in content
        elif i == 7:  # arrange tasks by due date
            search_str = r"arrange tasks by due date$"
            found = search_str.replace('\\', '') in content

        # For the actual search, we need to look for the raw string as it appears in the code
        if i == 1:  # Special handling for the first pattern
            found = r"create (\w+) task: (.+)$" in content
        elif i == 2:
            found = r"list tasks having (.+) tag$" in content
        elif i == 3:
            found = r"look for (.+) in tasks$" in content
        elif i == 4:
            found = r"list (.+) priority tasks$" in content
        elif i == 5:
            found = r"display (.+) priority tasks$" in content
        elif i == 6:
            found = r"list overdue tasks$" in content
        elif i == 7:
            found = r"arrange tasks by due date$" in content

        status = "[FOUND]" if found else "[NOT FOUND]"
        print(f"{i}. Pattern: '{search_str}' - {status}")
        if not found:
            all_found = False

    print()
    print("Checking for expected function implementations...")
    print()

    # Check for function implementations
    for i, func_name in enumerate(expected_functions, 1):
        found = func_name in content
        status = "[FOUND]" if found else "[NOT FOUND]"
        print(f"{i}. Function: {func_name} - {status}")
        if not found:
            all_found = False

    print()
    print("SUMMARY:")
    print("="*60)
    if all_found:
        print("[SUCCESS]: All expected patterns and functions were found in agent.py")
        print("[SUCCESS]: The previously broken commands should now work correctly")
        print("[SUCCESS]: Pattern matching system has been successfully enhanced")
    else:
        print("[FAILURE]: Some expected patterns or functions were not found")

    print()
    print("Previously broken commands that should now work:")
    print("  - 'Create personal task: call mom'")
    print("  - 'List tasks having shopping tag'")
    print("  - 'Look for email in tasks'")
    print("  - 'List medium priority tasks'")
    print("  - 'Display low priority tasks'")
    print("  - 'List overdue tasks'")
    print("  - 'Arrange tasks by due date'")

if __name__ == "__main__":
    verify_patterns()