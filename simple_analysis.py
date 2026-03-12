#!/usr/bin/env python3
"""
Simple analysis script to examine the functions directly in the agent.py file
"""

import re
import json


def extract_search_term(message_lower: str) -> str:
    """
    Replicate the search term extraction function from agent.py to test it
    """
    # Remove extra quotes and clean up the message
    # Handle cases where the message might have trailing quotes
    message_lower = re.sub(r'["\']+$', '', message_lower).strip()  # Remove trailing quotes

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
            search_term = match.group(1).strip()
            # Clean up the search term by removing trailing quotes
            search_term = re.sub(r'["\']+$', '', search_term).strip()
            # Clean up the search term
            search_term = re.sub(r'\btask[s]?\b', '', search_term).strip()

            # Special handling: if this looks like a tag-based request (e.g., "find work items"),
            # defer to tag filtering instead of search
            tag_items_match = re.match(r'(\w+)\s+items?$', search_term)
            if tag_items_match:
                potential_tag = tag_items_match.group(1)
                common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly', 'private', 'business'}
                if potential_tag in common_tags:
                    return None  # Let tag filtering handle this

            return search_term if search_term else None

    # Special handling for "find [item]" - exclude "find [tag] items" patterns
    # since those should be handled by tag filtering instead of search
    find_match = re.search(r'find ([^,.]+)', message_lower)
    if find_match:
        find_term = find_match.group(1).strip()
        # Clean up by removing trailing quotes
        find_term = re.sub(r'["\']+$', '', find_term).strip()

        # Check if it's in the format "find [tag] items", defer to tag filtering instead
        tag_items_match = re.match(r'(\w+)\s+items?$', find_term)
        if tag_items_match:
            potential_tag = tag_items_match.group(1)
            # Check if it's a common tag that should be filtered rather than searched
            common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly', 'private', 'business'}
            if potential_tag in common_tags:
                # This is likely a tag-based request, so return None to let tag filtering handle it
                return None
        # Otherwise, treat it as a regular search term
        find_term = re.sub(r'\btask[s]?\b', '', find_term).strip()
        return find_term if find_term else None

    # Also check for "find task with [term]" pattern but not "find [tag] items"
    find_with_match = re.search(r'find tasks? with ([^,.]+)', message_lower)
    if find_with_match:
        search_term = find_with_match.group(1).strip()
        # Clean up by removing trailing quotes
        search_term = re.sub(r'["\']+$', '', search_term).strip()
        search_term = re.sub(r'\btask[s]?\b', '', search_term).strip()
        return search_term if search_term else None

    # Also check for "search for X tasks" pattern
    if "search for" in message_lower:
        # Extract everything between "search for" and "tasks"
        search_match = re.search(r'search for (.+?) tasks?', message_lower)
        if search_match:
            search_term = search_match.group(1).strip()
            # Clean up by removing trailing quotes
            search_term = re.sub(r'["\']+$', '', search_term).strip()
            search_term = re.sub(r'\btask[s]?\b', '', search_term).strip()
            return search_term if search_term else None

    return None


def extract_tags_filter(message_lower: str) -> list:
    """
    Replicate the tags filter extraction function from agent.py to test it
    """
    # NEW: Handle combined filter pattern like "filter by tag work and priority high"
    combined_filter_pattern = r'filter by tag (\w+)(?: and priority \w+)?'
    combined_match = re.search(combined_filter_pattern, message_lower)
    if combined_match:
        potential_tag = combined_match.group(1)
        common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly', 'private', 'business'}
        if potential_tag in common_tags:
            return [potential_tag]

    # Look for tag patterns in filtering/searching contexts
    tag_patterns = [
        r'with tags ([^,.]+)',           # "with tags work, urgent"
        r'tag: ([^,.]+)',               # "tag: work"
        r'tagged with ([^,.]+)',         # "tagged with work"
        r'tags ([^,.]+)',               # "tags work, urgent"
        r'labeled ([^,.]+)',            # "labeled work"
        r'label: ([^,.]+)',             # "label: work"
        r'labels ([^,.]+)',             # "labels work, urgent"
        r'filter by tag ([^,.]+)',       # "filter by tag shopping" - NEW PATTERN
        r'filter by tags ([^,.]+)',      # "filter by tags work, urgent" - NEW PATTERN
        r'filter tasks? by tag ([^,.]+)', # "filter task by tag work" or "filter tasks by tag work"
    ]

    for pattern in tag_patterns:
        match = re.search(pattern, message_lower)
        if match:
            tag_text = match.group(1).strip()
            # Split tags by commas, semicolons, or ' and ' (with spaces around 'and')
            raw_tags = re.split(r'[,\s]+|;\s*|\s+and\s+', tag_text)
            tags = []
            for raw_tag in raw_tags:
                clean_tag = raw_tag.strip().lower()
                if clean_tag and clean_tag not in tags:
                    # Skip common words that shouldn't be tags
                    if clean_tag not in {'and', 'or', 'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to'}:
                        tags.append(clean_tag)
            return tags if tags else None

    # Handle specific patterns for "show [tag] tasks" and "find [tag] items"
    # Look for patterns like "show work tasks" or "find shopping items"
    show_pattern = re.search(r'show (\w+) tasks', message_lower)
    if show_pattern:
        potential_tag = show_pattern.group(1)
        # Only return if it's a common tag word
        common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly', 'private', 'business'}
        if potential_tag in common_tags:
            return [potential_tag]

    # Handle "show tasks with [tag] tag" pattern
    show_with_tag_pattern = re.search(r'show tasks with (\w+) tag', message_lower)
    if show_with_tag_pattern:
        potential_tag = show_with_tag_pattern.group(1)
        # Only return if it's a common tag word
        common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly', 'private', 'business'}
        if potential_tag in common_tags:
            return [potential_tag]

    find_pattern = re.search(r'find (\w+) items', message_lower)
    if find_pattern:
        potential_tag = find_pattern.group(1)
        # Only return if it's a common tag word
        common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly', 'private', 'business'}
        if potential_tag in common_tags:
            return [potential_tag]

    # Check for direct tag filtering like "work tasks", "shopping tasks"
    # This is more contextual - look for specific tag mentions
    if "work" in message_lower and any(phrase in message_lower for phrase in [
        "filter by", "show", "tasks with", "tasks tagged", "search for", "find"
    ]):
        # Check if "work" refers to a tag in this context
        if any(phrase in message_lower for phrase in [
            "work tasks", "work related tasks", "tasks for work", "work items"
        ]):
            return ["work"]

    if "shopping" in message_lower and any(phrase in message_lower for phrase in [
        "filter by", "show", "tasks with", "tasks tagged", "search for", "find"
    ]):
        if any(phrase in message_lower for phrase in [
            "shopping tasks", "shopping related tasks", "tasks for shopping", "shopping items"
        ]):
            return ["shopping"]

    # Additional context-aware tag detection for common patterns
    if "filter by" in message_lower and ("tag" in message_lower or "tags" in message_lower):
        # Extract potential tag after "filter by tag" or "filter by tags"
        filter_tag_match = re.search(r'filter by tag (\w+)', message_lower)
        if filter_tag_match:
            potential_tag = filter_tag_match.group(1)
            # Only return if it's a common tag word
            common_tags = {'work', 'home', 'personal', 'shopping', 'urgent', 'important', 'daily', 'weekly', 'private', 'business'}
            if potential_tag in common_tags:
                return [potential_tag]

    return None


def extract_task_details_for_update(message: str):
    """
    Replicate the task update extraction function from agent.py to test it
    """
    message_lower = message.lower()

    # NEW: Handle tag management commands first
    # Pattern for "add tag X to task Y"
    add_tag_pattern = r"add tag (\w+)\s+to task\s+(\d+)"
    add_tag_match = re.search(add_tag_pattern, message_lower)
    if add_tag_match:
        tag_to_add = add_tag_match.group(1).strip()
        task_number = add_tag_match.group(2).strip()
        # Return special format indicating tag operation
        return f"{task_number}_add_tag_{tag_to_add}", None, None

    # Pattern for "remove tag X from task Y"
    remove_tag_pattern = r"remove (\w+)\s+tag from task\s+(\d+)"
    remove_tag_match = re.search(remove_tag_pattern, message_lower)
    if remove_tag_match:
        tag_to_remove = remove_tag_match.group(1).strip()
        task_number = remove_tag_match.group(2).strip()
        # Return special format indicating tag removal operation
        return f"{task_number}_remove_tag_{tag_to_remove}", None, None

    return None, None, None


def enhanced_mock_response_check(message: str) -> bool:
    """
    Check if the enhanced_mock_response handles priority color help
    """
    message_lower = message.lower().strip()

    if "show me priority colors meaning" in message_lower or "show me priority color meaning" in message_lower or "priority colors meaning" in message_lower or "priority color" in message_lower or "colors meaning" in message_lower:
        return True  # This means the function should handle this
    return False


def analyze_system():
    """Analyze the current state of the system functionality"""
    print("ANALYZING TODO AI CHATBOT SYSTEM")
    print("=" * 70)

    print("\n1. SEARCH FUNCTIONALITY ANALYSIS")
    print("-" * 40)

    # Test cases that should work according to the requirements
    search_test_cases = [
        ("find milk", "milk"),
        ("look for fruits", "fruits"),
        ("search book", "book"),
        ("find report", "report"),
        ("find tasks with milk", "milk"),
        ('find milk"', 'milk'),  # Test with trailing quotes
        ('"find milk"', 'milk'),  # Test with surrounding quotes
    ]

    print("Testing search term extraction:")
    for input_msg, expected in search_test_cases:
        result = extract_search_term(input_msg.lower())
        status = "OK" if result == expected else "FAIL"
        print(f"  {status} Input: '{input_msg}' -> Output: '{result}' (Expected: '{expected}')")

    print("\n2. TAG FUNCTIONALITY ANALYSIS")
    print("-" * 40)

    # Test cases for tag extraction
    tag_test_cases = [
        ("show urgent tasks", ["urgent"]),
        ("show tasks tagged important", ["important"]),
        ("show work tasks", ["work"]),
        ("filter by tag work", ["work"]),
        ("filter by tag work and priority high", ["work"]),
        ("find work items", None),  # This should return None as it's tag-based
    ]

    print("Testing tag filter extraction:")
    for input_msg, expected in tag_test_cases:
        result = extract_tags_filter(input_msg.lower())
        status = "OK" if result == expected else "FAIL"
        print(f"  {status} Input: '{input_msg}' -> Output: {result} (Expected: {expected})")

    # Test "add tag" functionality
    print("\nTesting 'add tag' command parsing:")
    update_test_cases = [
        ("add important tag to task 1", ("1_add_tag_important", None, None)),
        ("add tag urgent to task 2", ("2_add_tag_urgent", None, None)),
        ("remove work tag from task 3", ("3_remove_tag_work", None, None)),
    ]

    for input_msg, expected in update_test_cases:
        result = extract_task_details_for_update(input_msg)
        status = "OK" if result == expected else "FAIL"
        print(f"  {status} Input: '{input_msg}' -> Output: {result} (Expected: {expected})")

    print("\n3. PRIORITY COLOR HELP ANALYSIS")
    print("-" * 40)

    help_queries = [
        "show me priority colors meaning",
        "show me priority color meaning",
        "priority colors meaning",
        "priority color",
        "colors meaning"
    ]

    print("Testing priority color help functionality:")
    for query in help_queries:
        result = enhanced_mock_response_check(query)
        status = "OK" if result else "FAIL"
        print(f"  {status} Query: '{query}' -> Handled: {result}")

    print("\n4. IDENTIFIED ISSUES")
    print("-" * 40)

    print("\nCRITICAL FINDINGS:")
    print("1. Search functionality should work for 'find milk', 'look for fruits', etc.")
    print("2. Tag functionality should distinguish between tag-based and search queries")
    print("3. 'Add tag' commands should create tag operations, not new tasks")
    print("4. Priority color help should respond to color-related queries")

    print("\nANALYSIS:")
    print("1. The code appears to have implemented the features, but they might not be working due to:")
    print("  a) The function calls in the main agent flow might not be reaching these functions")
    print("  b) Regex patterns might not match the expected input exactly")
    print("  c) The control flow in invoke_agent() might not be calling the right functions")
    print("  d) There might be logical errors in the function calls or return values")

    print("\nPOTENTIAL ROOT CAUSES:")
    print("1. Main control flow in invoke_agent() might have bugs in pattern matching order")
    print("2. The regex patterns for detecting 'add tag' commands might not be specific enough")
    print("3. Tag vs Search disambiguation might not work as expected")
    print("4. Task creation vs tag assignment might have conflicting patterns")

    print("\nRECOMMENDATION:")
    print("- Need to examine the invoke_agent() function more closely")
    print("- Check if the pattern matching order causes conflicts")
    print("- Verify that 'add tag' commands are not being misinterpreted as 'add task' commands")


if __name__ == "__main__":
    analyze_system()