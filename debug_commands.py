#!/usr/bin/env python3
"""
Debug script to test the specific failing commands and analyze the pattern matching
"""

import re


def debug_extract_search_term(message_lower: str) -> str:
    """
    Debug version of the search term extraction function to see what's happening
    """
    print(f"  DEBUG: Input message_lower = '{message_lower}'")

    # Remove extra quotes and clean up the message
    # Handle cases where the message might have trailing quotes
    original_message = message_lower
    message_lower = re.sub(r'["\']+$', '', message_lower).strip()  # Remove trailing quotes

    if original_message != message_lower:
        print(f"  DEBUG: After quote removal: '{message_lower}'")

    # Look for search patterns
    search_patterns = [
        r'look for ([^,.]+)',           # "look for groceries" - NEW: Added this for requirement
        r'search for ([^,.]+)',         # "search for groceries"
        r'search tasks? with ([^,.]+)', # "search task with groceries"
        r'find tasks? with ([^,.]+)',   # "find tasks with milk" - NEW: Added for requirement
    ]

    for pattern in search_patterns:
        match = re.search(pattern, message_lower)
        if match:
            print(f"  DEBUG: Matched pattern '{pattern}' with group: '{match.group(1)}'")
            search_term = match.group(1).strip()
            # Clean up the search term by removing trailing quotes
            search_term = re.sub(r'["\']+$', '', search_term).strip()
            # Clean up the search term
            search_term = re.sub(r'\btask[s]?\b', '', search_term).strip()

            print(f"  DEBUG: Final search term after cleaning: '{search_term}'")

            # Special handling: if this looks like a tag-based request (e.g., "find work items"),
            # defer to tag filtering instead of search
            tag_items_match = re.match(r'(\w+)\s+items?$', search_term)
            if tag_items_match:
                potential_tag = tag_items_match.group(1)
                common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly', 'private', 'business'}
                if potential_tag in common_tags:
                    print(f"  DEBUG: Defer to tag filtering for tag: '{potential_tag}'")
                    return None  # Let tag filtering handle this

            return search_term if search_term else None

    # Special handling for "find [item]" - exclude "find [tag] items" patterns
    # since those should be handled by tag filtering instead of search
    find_match = re.search(r'find ([^,.]+)', message_lower)
    if find_match:
        print(f"  DEBUG: Found 'find' pattern with group: '{find_match.group(1)}'")
        find_term = find_match.group(1).strip()
        # Clean up by removing trailing quotes
        find_term = re.sub(r'["\']+$', '', find_term).strip()

        print(f"  DEBUG: After quote cleaning: '{find_term}'")

        # Check if it's in the format "find [tag] items", defer to tag filtering instead
        tag_items_match = re.match(r'(\w+)\s+items?$', find_term)
        if tag_items_match:
            potential_tag = tag_items_match.group(1)
            # Check if it's a common tag that should be filtered rather than searched
            common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly', 'private', 'business'}
            if potential_tag in common_tags:
                # This is likely a tag-based request, so return None to let tag filtering handle it
                print(f"  DEBUG: Defer to tag filtering for tag: '{potential_tag}'")
                return None
        # Otherwise, treat it as a regular search term
        find_term = re.sub(r'\btask[s]?\b', '', find_term).strip()
        print(f"  DEBUG: Final find term: '{find_term}'")
        return find_term if find_term else None

    # Also check for "find task with [term]" pattern but not "find [tag] items"
    find_with_match = re.search(r'find tasks? with ([^,.]+)', message_lower)
    if find_with_match:
        print(f"  DEBUG: Found 'find with' pattern with group: '{find_with_match.group(1)}'")
        search_term = find_with_match.group(1).strip()
        # Clean up by removing trailing quotes
        search_term = re.sub(r'["\']+$', '', search_term).strip()
        search_term = re.sub(r'\btask[s]?\b', '', search_term).strip()
        print(f"  DEBUG: Final find with term: '{search_term}'")
        return search_term if search_term else None

    # Also check for "search for X tasks" pattern
    if "search for" in message_lower:
        # Extract everything between "search for" and "tasks"
        search_match = re.search(r'search for (.+?) tasks?', message_lower)
        if search_match:
            print(f"  DEBUG: Found 'search for' pattern with group: '{search_match.group(1)}'")
            search_term = search_match.group(1).strip()
            # Clean up by removing trailing quotes
            search_term = re.sub(r'["\']+$', '', search_term).strip()
            search_term = re.sub(r'\btask[s]?\b', '', search_term).strip()
            print(f"  DEBUG: Final search for term: '{search_term}'")
            return search_term if search_term else None

    print("  DEBUG: No search pattern matched")
    return None


def debug_extract_task_details_for_update(message: str):
    """
    Debug version of the task update extraction function
    """
    print(f"  DEBUG: Input message = '{message}'")
    message_lower = message.lower()

    # NEW: Handle tag management commands first
    # Pattern for "add tag X to task Y"
    add_tag_pattern = r"add tag (\w+)\s+to task\s+(\d+)"
    add_tag_match = re.search(add_tag_pattern, message_lower)
    if add_tag_match:
        print(f"  DEBUG: Matched add tag pattern: tag='{add_tag_match.group(1)}', task='{add_tag_match.group(2)}'")
        tag_to_add = add_tag_match.group(1).strip()
        task_number = add_tag_match.group(2).strip()
        # Return special format indicating tag operation
        result = f"{task_number}_add_tag_{tag_to_add}", None, None
        print(f"  DEBUG: Result = {result}")
        return result

    # Pattern for "remove tag X from task Y"
    remove_tag_pattern = r"remove (\w+)\s+tag from task\s+(\d+)"
    remove_tag_match = re.search(remove_tag_pattern, message_lower)
    if remove_tag_match:
        print(f"  DEBUG: Matched remove tag pattern: tag='{remove_tag_match.group(1)}', task='{remove_tag_match.group(2)}'")
        tag_to_remove = remove_tag_match.group(1).strip()
        task_number = remove_tag_match.group(2).strip()
        # Return special format indicating tag removal operation
        result = f"{task_number}_remove_tag_{tag_to_remove}", None, None
        print(f"  DEBUG: Result = {result}")
        return result

    print("  DEBUG: No tag management pattern matched")
    return None, None, None


def debug_invoke_agent_logic(user_message: str):
    """
    Simulate the invoke_agent logic to see which patterns match
    """
    print(f"\nANALYZING COMMAND: '{user_message}'")
    user_message_lower = user_message.lower().strip()

    # FIRST check: search patterns ('find ', 'search ', 'look for ')
    print("  Checking FIRST: search patterns")
    search_patterns = ['find ', 'search ', 'look for ']
    has_search_pattern = any(pattern in user_message_lower for pattern in search_patterns)
    print(f"    Has search pattern: {has_search_pattern}")

    if has_search_pattern:
        print("    -> Would go to search handling")
        search_result = debug_extract_search_term(user_message_lower)
        print(f"    -> Search result: {search_result}")
        return "search", search_result

    # SECOND: tag patterns ('add.*tag.*task')
    print("  Checking SECOND: tag patterns")
    import re
    tag_pattern = r'add.*tag.*task'
    has_tag_pattern = bool(re.search(tag_pattern, user_message_lower))
    print(f"    Has tag pattern '{tag_pattern}': {has_tag_pattern}")

    if has_tag_pattern:
        print("    -> Would go to tag handling")
        tag_result = debug_extract_task_details_for_update(user_message)
        print(f"    -> Tag result: {tag_result}")
        return "tag", tag_result

    # Check other tag patterns too
    other_tag_pattern = r'remove.*tag.*task'
    has_other_tag_pattern = bool(re.search(other_tag_pattern, user_message_lower))
    print(f"    Has remove tag pattern '{other_tag_pattern}': {has_other_tag_pattern}")

    if has_other_tag_pattern:
        print("    -> Would go to tag handling (remove)")
        tag_result = debug_extract_task_details_for_update(user_message)
        print(f"    -> Tag result: {tag_result}")
        return "tag", tag_result

    # THIRD: help patterns ('red means' or 'color mean')
    print("  Checking THIRD: help patterns")
    help_patterns = ['red means', 'color mean']
    has_help_pattern = any(pattern in user_message_lower for pattern in help_patterns)
    print(f"    Has help pattern: {has_help_pattern}")

    if has_help_pattern:
        print("    -> Would go to help handling")
        return "help", True

    # FOURTH: filter pattern ('show' + 'priority' or 'work')
    print("  Checking FOURTH: filter patterns")
    has_show = 'show' in user_message_lower
    has_priority_or_work = 'priority' in user_message_lower or 'work' in user_message_lower
    has_filter_pattern = has_show and has_priority_or_work
    print(f"    Has 'show': {has_show}, has 'priority'/'work': {has_priority_or_work}")
    print(f"    Has filter pattern: {has_filter_pattern}")

    if has_filter_pattern:
        print("    -> Would go to filter handling")
        return "filter", True

    print("  -> Would go to default/fallback handling")
    return "fallback", None


def test_debugging():
    """Test the specific commands that are failing"""
    print("DEBUGGING SPECIFIC COMMANDS")
    print("=" * 60)

    test_commands = [
        "find milk",
        "add urgent tag to task 1",
        "red means what",
        "show high priority work"
    ]

    for cmd in test_commands:
        print(f"\n{'='*60}")
        result_type, result = debug_invoke_agent_logic(cmd)
        print(f"FINAL RESULT for '{cmd}': {result_type} -> {result}")

    print(f"\n{'='*60}")
    print("ANALYSIS:")
    print("1. 'find milk' - Check if search pattern matches")
    print("2. 'add urgent tag to task 1' - Check if tag pattern matches")
    print("3. 'red means what' - Check if help pattern matches")
    print("4. 'show high priority work' - Check if filter pattern matches")


if __name__ == "__main__":
    test_debugging()