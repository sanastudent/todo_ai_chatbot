#!/usr/bin/env python3
"""
Direct test of the regex patterns to see if they work correctly
"""

import re


def test_search_patterns():
    """Test the search patterns directly"""
    print(">> TESTING SEARCH PATTERNS")
    print("=" * 50)

    search_patterns = ['find ', 'search ', 'look for ']

    test_messages = [
        "find milk",
        "search book",
        "look for fruits",
        "find report",
        "add task to buy milk",
        "show my tasks"
    ]

    for msg in test_messages:
        msg_lower = msg.lower()
        has_search_pattern = any(pattern in msg_lower for pattern in search_patterns)
        print(f"Message: '{msg}' -> Has search pattern: {has_search_pattern}")

        if has_search_pattern:
            # Find which pattern matched
            for pattern in search_patterns:
                if pattern in msg_lower:
                    print(f"  -> Matched pattern: '{pattern}'")
                    break


def test_tag_patterns():
    """Test the tag patterns directly"""
    print("\nTAG  TESTING TAG PATTERNS")
    print("=" * 50)

    # Test the extract_task_details_for_update function logic
    def extract_task_details_for_update(message: str):
        message_lower = message.lower()

        # Pattern for "add [tag_name] tag to task [number]" (e.g., "add urgent tag to task 1", "add work tag to task 2")
        add_tag_pattern = r"add\s+(\w+)\s+tag\s+to\s+task\s+(\d+)"
        add_tag_match = re.search(add_tag_pattern, message_lower)
        if add_tag_match:
            tag_to_add = add_tag_match.group(1).strip()
            task_number = add_tag_match.group(2).strip()
            # Return special format indicating tag operation
            return f"{task_number}_add_tag_{tag_to_add}", None, None

        # Pattern for "remove [tag_name] tag from task [number]" (e.g., "remove urgent tag from task 1", "remove work tag from task 2")
        remove_tag_pattern = r"remove\s+(\w+)\s+tag\s+from\s+task\s+(\d+)"
        remove_tag_match = re.search(remove_tag_pattern, message_lower)
        if remove_tag_match:
            tag_to_remove = remove_tag_match.group(1).strip()
            task_number = remove_tag_match.group(2).strip()
            # Return special format indicating tag removal operation
            return f"{task_number}_remove_tag_{tag_to_remove}", None, None

        return None, None, None

    test_messages = [
        "add urgent tag to task 1",
        "remove work tag from task 2",
        "add important tag to task 3",
        "find milk",
        "show high priority work"
    ]

    for msg in test_messages:
        result, _, _ = extract_task_details_for_update(msg)
        has_tag_pattern = result is not None
        print(f"Message: '{msg}' -> Has tag pattern: {has_tag_pattern}")
        if has_tag_pattern:
            print(f"  -> Result: '{result}'")


def test_help_patterns():
    """Test the help patterns directly"""
    print("\nHELP TESTING HELP PATTERNS")
    print("=" * 50)

    help_phrases = [
        "help", "what can you do", "assist", "commands", "features",
        "priority color", "color mean", "red means", "show me priority colors meaning",
        "show me priority color meaning", "priority colors meaning", "colors meaning"
    ]

    test_messages = [
        "red means what",
        "show me priority colors meaning",
        "help me",
        "what can you do",
        "find milk",
        "add urgent tag to task 1"
    ]

    for msg in test_messages:
        msg_lower = msg.lower()
        has_help_pattern = any(phrase in msg_lower for phrase in help_phrases)
        print(f"Message: '{msg}' -> Has help pattern: {has_help_pattern}")

        if has_help_pattern:
            # Find which phrase matched
            for phrase in help_phrases:
                if phrase in msg_lower:
                    print(f"  -> Matched phrase: '{phrase}'")
                    break


def test_filter_patterns():
    """Test the filter patterns directly"""
    print("\nFILT TESTING FILTER PATTERNS")
    print("=" * 50)

    test_messages = [
        "show high priority work",
        "show work tasks",
        "show high priority",
        "find milk",
        "add urgent tag to task 1"
    ]

    for msg in test_messages:
        msg_lower = msg.lower()
        has_show = 'show' in msg_lower
        has_priority_or_work = 'priority' in msg_lower or 'work' in msg_lower
        has_filter_pattern = has_show and has_priority_or_work

        print(f"Message: '{msg}' -> Has show: {has_show}, has priority/work: {has_priority_or_work}, Combined: {has_filter_pattern}")


def simulate_full_flow():
    """Simulate the full invoke_agent flow"""
    print("\n🔄 SIMULATING FULL FLOW")
    print("=" * 50)

    def extract_task_details_for_update(message: str):
        message_lower = message.lower()

        # Pattern for "add [tag_name] tag to task [number]" (e.g., "add urgent tag to task 1", "add work tag to task 2")
        add_tag_pattern = r"add\s+(\w+)\s+tag\s+to\s+task\s+(\d+)"
        add_tag_match = re.search(add_tag_pattern, message_lower)
        if add_tag_match:
            tag_to_add = add_tag_match.group(1).strip()
            task_number = add_tag_match.group(2).strip()
            # Return special format indicating tag operation
            return f"{task_number}_add_tag_{tag_to_add}", None, None

        # Pattern for "remove [tag_name] tag from task [number]" (e.g., "remove urgent tag from task 1", "remove work tag from task 2")
        remove_tag_pattern = r"remove\s+(\w+)\s+tag\s+from\s+task\s+(\d+)"
        remove_tag_match = re.search(remove_tag_pattern, message_lower)
        if remove_tag_match:
            tag_to_remove = remove_tag_match.group(1).strip()
            task_number = remove_tag_match.group(2).strip()
            # Return special format indicating tag removal operation
            return f"{task_number}_remove_tag_{tag_to_remove}", None, None

        return None, None, None

    test_commands = [
        "find milk",
        "add urgent tag to task 1",
        "red means what",
        "show high priority work"
    ]

    for cmd in test_commands:
        print(f"\nCommand: '{cmd}'")
        msg_lower = cmd.lower()

        # FIRST: Search patterns
        search_patterns = ['find ', 'search ', 'look for ']
        has_search = any(pattern in msg_lower for pattern in search_patterns)
        print(f"  Search: {has_search}")

        if has_search:
            print(f"    -> Would go to SEARCH handling")
            continue

        # SECOND: Tag patterns
        task_result, _, _ = extract_task_details_for_update(cmd)
        has_tag = task_result is not None
        print(f"  Tag: {has_tag}")

        if has_tag:
            print(f"    -> Would go to TAG handling: {task_result}")
            continue

        # THIRD: Help patterns
        help_phrases = [
            "help", "what can you do", "assist", "commands", "features",
            "priority color", "color mean", "red means", "show me priority colors meaning",
            "show me priority color meaning", "priority colors meaning", "colors meaning"
        ]
        has_help = any(phrase in msg_lower for phrase in help_phrases)
        print(f"  Help: {has_help}")

        if has_help:
            print(f"    -> Would go to HELP handling")
            continue

        # FOURTH: Filter patterns
        has_show = 'show' in msg_lower
        has_priority_or_work = 'priority' in msg_lower or 'work' in msg_lower
        has_filter = has_show and has_priority_or_work
        print(f"  Filter: {has_filter}")

        if has_filter:
            print(f"    -> Would go to FILTER handling")
            continue

        # Default: fallback
        print(f"    -> Would go to FALLBACK handling")


if __name__ == "__main__":
    test_search_patterns()
    test_tag_patterns()
    test_help_patterns()
    test_filter_patterns()
    simulate_full_flow()

    print(f"\n{'='*50}")
    print("PATTERN ANALYSIS COMPLETE")
    print("All patterns seem to work correctly in isolation!")