#!/usr/bin/env python3
"""
Test script to analyze how the current regex patterns handle problematic queries.
"""

import re

def analyze_command_patterns():
    """Analyze how current patterns match the problematic queries."""

    # These are the patterns extracted from the agent.py file
    patterns = {
        # Update patterns (from lines ~1684-1788)
        "update_numbered": r"(?:update|change|modify)\s+(?:task\s+)?(?:number\s+|#)?(\d+)\s+to\s+(.+)",

        # Various change/update patterns (from lines ~1696-1788)
        "change_quoted": r"change ['\"](.+?)['\"] to ['\"](.+?)['\"]",
        "update_quoted": r"update ['\"](.+?)['\"] to ['\"](.+?)['\"]",
        "modify_quoted": r"modify ['\"](.+?)['\"] to ['\"](.+?)['\"]",
        "change_general": r"change (.+?) to (.+)",
        "update_general": r"update (.+?) to (.+)",
        "modify_general": r"modify (.+?) to (.+)",
        "update_description": r"update ['\"](.+?)['\"] description to ['\"](.+?)['\"]",
        "update_desc_general": r"update (.+?) description to (.+)",
        "change_title_desc": r"change ['\"](.+?)['\"] title to ['\"](.+?)['\"] and description to ['\"](.+?)['\"]",
        "update_title_desc": r"update ['\"](.+?)['\"] title to ['\"](.+?)['\"] and description to ['\"](.+?)['\"]",
        "rename_quoted": r"rename ['\"](.+?)['\"] to ['\"](.+?)['\"]",
        "rename_general": r"rename (.+?) to (.+)",

        # List/filter patterns (from lines ~378-388)
        "show_category_tasks": r'show (\w+) tasks',
        "show_tasks_with_tag": r'show tasks with (\w+) tag',
        "find_category_items": r'find (\w+) items',

        # Search patterns (from various lines)
        "search_tasks": r'search (?:for )?(.+?) tasks?',
        "find_tasks": r'find (?:tasks? )?(?:with |containing |about )?(.+)',

        # Due date patterns (from lines ~2269-2278)
        "due_date_patterns": [
            r'due (?:today|now|immediately)',
            r'due tomorrow',
            r'due (?:in )?\d+ (?:days?|weeks?|months?)',
            r'due (?:by |on )?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'due (?:by |on )?(?:january|february|march|april|may|june|july|august|september|october|november|december)'
        ],

        # Sort patterns (from various lines in agent.py)
        "sort_patterns": [
            r'order (?:tasks? )?by (.+)',
            r'sort (?:tasks? )?by (.+)',
            r'arrange (?:tasks? )?by (.+)'
        ]
    }

    # Problematic queries to test
    test_queries = [
        "change task 3 to medium priority",
        "list personal tasks",
        "find tasks tagged urgent",
        "search tasks for meeting",
        "tasks due today",
        "order tasks by title"
    ]

    print("Analyzing command patterns against problematic queries:")
    print("=" * 60)

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 30)

        matched = False

        for pattern_name, pattern in patterns.items():
            if isinstance(pattern, list):
                for i, sub_pattern in enumerate(pattern):
                    match = re.search(sub_pattern, query.lower())
                    if match:
                        print(f"  MATCH [{pattern_name}_{i}]: {sub_pattern}")
                        print(f"    Groups: {match.groups()}")
                        matched = True
            else:
                match = re.search(pattern, query.lower())
                if match:
                    print(f"  MATCH [{pattern_name}]: {pattern}")
                    print(f"    Groups: {match.groups()}")
                    matched = True

        if not matched:
            print("  NO MATCH - Query not handled by current patterns")

    print("\n" + "=" * 60)
    print("Analysis complete.")

def analyze_specific_patterns():
    """Analyze specific patterns that should handle the problematic queries."""
    print("\nDetailed analysis of specific pattern categories:")
    print("=" * 60)

    # Test the first problematic query: "change task 3 to medium priority"
    query1 = "change task 3 to medium priority"
    print(f"\nQuery 1: '{query1}'")

    # This should match the numbered update pattern
    update_numbered = r"(?:update|change|modify)\s+(?:task\s+)?(?:number\s+|#)?(\d+)\s+to\s+(.+)"
    match = re.search(update_numbered, query1.lower())
    if match:
        print(f"  [YES] Matches numbered update pattern: {update_numbered}")
        print(f"    Task ID: {match.group(1)}, New value: {match.group(2)}")
    else:
        print(f"  [NO] Does NOT match numbered update pattern: {update_numbered}")

    # Test second query: "list personal tasks"
    query2 = "list personal tasks"
    print(f"\nQuery 2: '{query2}'")

    # This should match show category tasks pattern
    show_category = r'show (\w+) tasks'
    match = re.search(show_category, query2.lower())
    if match:
        print(f"  [YES] Matches show category pattern: {show_category}")
        print(f"    Category: {match.group(1)}")
    else:
        print(f"  [NO] Does NOT match show category pattern: {show_category}")

    # But "list" instead of "show" - let's try a more general pattern
    list_category = r'(?:show|list) (\w+) tasks?'
    match = re.search(list_category, query2.lower())
    if match:
        print(f"  [YES] Matches extended list/show category pattern: {list_category}")
        print(f"    Category: {match.group(1)}")
    else:
        print(f"  [NO] Does NOT match extended list/show category pattern: {list_category}")

    # Test third query: "find tasks tagged urgent"
    query3 = "find tasks tagged urgent"
    print(f"\nQuery 3: '{query3}'")

    # This might match tag patterns - let's look for tag-related patterns
    tag_pattern = r'tasks tagged (\w+)'
    match = re.search(tag_pattern, query3.lower())
    if match:
        print(f"  [YES] Matches tag pattern: {tag_pattern}")
        print(f"    Tag: {match.group(1)}")
    else:
        print(f"  [NO] Does NOT match tag pattern: {tag_pattern}")

    # Test fourth query: "search tasks for meeting"
    query4 = "search tasks for meeting"
    print(f"\nQuery 4: '{query4}'")

    search_pattern = r'search (?:for )?(.+?) tasks?'
    match = re.search(search_pattern, query4.lower())
    if match:
        print(f"  [YES] Matches search pattern: {search_pattern}")
        print(f"    Search term: {match.group(1)}")
    else:
        print(f"  [NO] Does NOT match search pattern: {search_pattern}")

    # Test fifth query: "tasks due today"
    query5 = "tasks due today"
    print(f"\nQuery 5: '{query5}'")

    due_pattern = r'due (?:today|now|immediately)'
    match = re.search(due_pattern, query5.lower())
    if match:
        print(f"  [YES] Matches due date pattern: {due_pattern}")
    else:
        print(f"  [NO] Does NOT match due date pattern: {due_pattern}")

    # Test sixth query: "order tasks by title"
    query6 = "order tasks by title"
    print(f"\nQuery 6: '{query6}'")

    sort_pattern = r'(?:order|sort|arrange) (?:tasks? )?by (.+)'
    match = re.search(sort_pattern, query6.lower())
    if match:
        print(f"  [YES] Matches sort pattern: {sort_pattern}")
        print(f"    Sort by: {match.group(1)}")
    else:
        print(f"  [NO] Does NOT match sort pattern: {sort_pattern}")

if __name__ == "__main__":
    analyze_command_patterns()
    analyze_specific_patterns()