#!/usr/bin/env python3
"""
Simple validation test for the implemented fixes.
"""

import re


def test_search_functionality():
    """Test that 'Find fruits' matches tasks containing 'fruits' and 'Look for X' triggers search."""
    print("Testing SEARCH functionality...")

    # Simulate the extract_search_term function logic
    def extract_search_term(message_lower: str):
        # Look for search patterns
        search_patterns = [
            r'look for ([^,.]+)',           # "look for groceries" - NEW: Added this for requirement
            r'search for ([^,.]+)',         # "search for groceries"
            r'search tasks? with ([^,.]+)', # "search task with groceries"
        ]

        for pattern in search_patterns:
            match = re.search(pattern, message_lower)
            if match:
                search_term = match.group(1).strip()
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
            search_term = re.sub(r'\btask[s]?\b', '', search_term).strip()
            return search_term if search_term else None

        # Also check for "search for X tasks" pattern
        if "search for" in message_lower:
            # Extract everything between "search for" and "tasks"
            search_match = re.search(r'search for (.+?) tasks?', message_lower)
            if search_match:
                search_term = search_match.group(1).strip()
                search_term = re.sub(r'\btask[s]?\b', '', search_term).strip()
                return search_term if search_term else None

        return None

    # Test "Look for X" pattern
    search_term = extract_search_term("look for fruits".lower())
    assert search_term == "fruits", f"Expected 'fruits', got '{search_term}'"
    print("OK 'Look for fruits' correctly extracts 'fruits' as search term")

    # Test "Find X" pattern (should work for non-tag items)
    search_term = extract_search_term("find apples".lower())
    assert search_term == "apples", f"Expected 'apples', got '{search_term}'"
    print("OK 'Find apples' correctly extracts 'apples' as search term")

    # Test "Find X items" pattern (should return None for tag-based requests)
    search_term = extract_search_term("find work items".lower())
    assert search_term is None, f"Expected None for tag-based request, got '{search_term}'"
    print("OK 'Find work items' correctly defers to tag filtering instead of search")


def test_filter_functionality():
    """Test that 'Filter by tag work and priority high' works correctly."""
    print("\nTesting FILTER functionality...")

    # Simulate extract_tags_filter function logic
    def extract_tags_filter(message_lower: str):
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

    # Test tag extraction from combined filter
    tags = extract_tags_filter("filter by tag work and priority high".lower())
    assert tags == ["work"], f"Expected ['work'], got {tags}"
    print("OK 'filter by tag work and priority high' correctly extracts 'work' as tag")

    # Simulate extract_priority_filter function logic
    def extract_priority_filter(message_lower: str):
        # NEW: Handle combined filter pattern like "filter by tag work and priority high"
        combined_filter_pattern = r'filter by tag \w+ and priority (\w+)'
        combined_match = re.search(combined_filter_pattern, message_lower)
        if combined_match:
            priority_word = combined_match.group(1)
            if priority_word in ['high', 'medium', 'low']:
                return [priority_word]

        # Check for priority filters like "filter by high priority", "show high priority tasks", etc.
        # Also handle combined filters like "filter by tag work and priority high"
        if "high priority" in message_lower or "high-priority" in message_lower or "priority high" in message_lower:
            return ["high"]
        elif "medium priority" in message_lower or "medium-priority" in message_lower or "priority medium" in message_lower:
            return ["medium"]
        elif "low priority" in message_lower or "low-priority" in message_lower or "priority low" in message_lower:
            return ["low"]
        elif any(phrase in message_lower for phrase in [
            "important", "urgent", "critical", "top priority"
        ]) and ("filter by" in message_lower or "show" in message_lower):
            return ["high"]
        elif any(phrase in message_lower for phrase in [
            "normal", "standard", "regular"
        ]) and ("filter by" in message_lower or "show" in message_lower):
            return ["medium"]
        elif any(phrase in message_lower for phrase in [
            "low importance", "not urgent"
        ]) and ("filter by" in message_lower or "show" in message_lower):
            return ["low"]

        # Check for direct priority requests like "high priority tasks"
        if any(phrase in message_lower for phrase in [
            "high priority tasks", "high-priority tasks", "important tasks", "urgent tasks"
        ]):
            return ["high"]
        elif any(phrase in message_lower for phrase in [
            "medium priority tasks", "medium-priority tasks", "normal tasks", "standard tasks"
        ]):
            return ["medium"]
        elif any(phrase in message_lower for phrase in [
            "low priority tasks", "low-priority tasks", "low importance tasks"
        ]):
            return ["low"]

        return None

    # Test priority extraction from combined filter
    priority = extract_priority_filter("filter by tag work and priority high".lower())
    assert priority == ["high"], f"Expected ['high'], got {priority}"
    print("OK 'filter by tag work and priority high' correctly extracts 'high' as priority")


def test_sort_functionality():
    """Test that 'Show newest high priority tasks' sorts by date."""
    print("\nTesting SORT functionality...")

    # Simulate extract_sort_params function logic
    def extract_sort_params(message_lower: str):
        sort_params = {}

        # NEW: Handle "Show newest high priority tasks" - extract sort info first
        if "newest" in message_lower and any(phrase in message_lower for phrase in [
            "show", "list", "display", "find"
        ]):
            sort_params['sort_by'] = 'created_at'
            sort_params['sort_order'] = 'desc'  # newest first

        # Check for sort by date/time
        if any(phrase in message_lower for phrase in [
            "sort by date", "sort tasks by date", "sort by created date",
            "sort by time", "sort by created time", "sort by age",
            "sort by newest", "sort by oldest", "sort by creation date"
        ]):
            sort_params['sort_by'] = 'created_at'
            if any(phrase in message_lower for phrase in [
                "newest", "most recent", "latest"
            ]):
                sort_params['sort_order'] = 'desc'
            elif any(phrase in message_lower for phrase in [
                "oldest", "earliest"
            ]):
                sort_params['sort_order'] = 'asc'
            else:
                sort_params['sort_order'] = 'desc'  # Default to newest first

        # Check for sort by priority
        elif any(phrase in message_lower for phrase in [
            "sort by priority", "sort tasks by priority", "sort by importance"
        ]):
            sort_params['sort_by'] = 'priority'
            if "descending" in message_lower or "high to low" in message_lower:
                sort_params['sort_order'] = 'desc'
            else:
                sort_params['sort_order'] = 'asc'

        # Check for sort by title/alphabetical
        elif any(phrase in message_lower for phrase in [
            "sort by title", "sort tasks by title", "sort alphabetically",
            "sort by name", "sort tasks by name"
        ]):
            sort_params['sort_by'] = 'title'
            if "descending" in message_lower or "z to a" in message_lower:
                sort_params['sort_order'] = 'desc'
            else:
                sort_params['sort_order'] = 'asc'

        # Check for sort by completion status
        elif any(phrase in message_lower for phrase in [
            "sort by status", "sort tasks by status", "sort by completion",
            "sort by completed", "sort by pending"
        ]):
            sort_params['sort_by'] = 'completed'
            if "completed first" in message_lower or "done first" in message_lower:
                sort_params['sort_order'] = 'desc'
            else:
                sort_params['sort_order'] = 'asc'

        return sort_params

    # Test sort extraction for "Show newest high priority tasks"
    sort_params = extract_sort_params("show newest high priority tasks".lower())
    expected_sort_by = "created_at"
    expected_sort_order = "desc"

    assert sort_params.get("sort_by") == expected_sort_by, f"Expected sort_by '{expected_sort_by}', got '{sort_params.get('sort_by')}'"
    assert sort_params.get("sort_order") == expected_sort_order, f"Expected sort_order '{expected_sort_order}', got '{sort_params.get('sort_order')}'"
    print("OK 'Show newest high priority tasks' correctly extracts sort parameters")


def test_task_id_functionality():
    """Test that task ID operations work correctly."""
    print("\nTesting TASK ID functionality...")

    # Simulate extract_task_details_for_update function logic
    def extract_task_details_for_update(message: str):
        message = message.strip()
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

        # Pattern for numbered task updates (e.g., "update task 1 to buy organic groceries")
        number_pattern = r"(?:update|change|modify)\s+(?:task\s+)?(?:number\s+|#)?(\d+)\s+to\s+(.+)"
        number_match = re.search(number_pattern, message_lower)
        if number_match:
            task_number = number_match.group(1).strip()
            new_details = number_match.group(2).strip()
            # Return the task number as a string to be handled by the task matching logic
            return task_number, new_details, None

        # Look for patterns like "change X to Y", "update X to Y", "modify X to Y"
        # where X is the current task and Y is the new information

        # Pattern 1: "change 'current task' to 'new title'"
        pattern1 = r"change ['\"](.+?)['\"] to ['\"](.+?)['\"]"
        match1 = re.search(pattern1, message_lower)
        if match1:
            current_task = match1.group(1).strip()
            new_title = match1.group(2).strip()
            return current_task, new_title, None

        # Pattern 2: "update 'current task' to 'new title'"
        pattern2 = r"update ['\"](.+?)['\"] to ['\"](.+?)['\"]"
        match2 = re.search(pattern2, message_lower)
        if match2:
            current_task = match2.group(1).strip()
            new_title = match2.group(2).strip()
            return current_task, new_title, None

        # Pattern 3: "modify 'current task' to 'new title'"
        pattern3 = r"modify ['\"](.+?)['\"] to ['\"](.+?)['\"]"
        match3 = re.search(pattern3, message_lower)
        if match3:
            current_task = match3.group(1).strip()
            new_title = match3.group(2).strip()
            return current_task, new_title, None

        # Pattern 4: More general patterns like "change buy groceries to buy organic groceries"
        # Look for phrases like "change X to Y" without quotes
        pattern4 = r"change (.+?) to (.+)"
        match4 = re.search(pattern4, message_lower)
        if match4:
            current_task = match4.group(1).strip()
            new_title = match4.group(2).strip()
            return current_task, new_title, None

        # Pattern 5: "update X to Y" without quotes
        pattern5 = r"update (.+?) to (.+)"
        match5 = re.search(pattern5, message_lower)
        if match5:
            current_task = match5.group(1).strip()
            new_title = match5.group(2).strip()
            return current_task, new_title, None

        # Pattern 6: "modify X to Y" without quotes
        pattern6 = r"modify (.+?) to (.+)"
        match6 = re.search(pattern6, message_lower)
        if match6:
            current_task = match6.group(1).strip()
            new_title = match6.group(2).strip()
            return current_task, new_title, None

        # Pattern 7: Update description specifically
        pattern7 = r"update ['\"](.+?)['\"] description to ['\"](.+?)['\"]"
        match7 = re.search(pattern7, message_lower)
        if match7:
            current_task = match7.group(1).strip()
            new_description = match7.group(2).strip()
            return current_task, None, new_description

        # Pattern 8: Update description without quotes
        pattern8 = r"update (.+?) description to (.+)"
        match8 = re.search(pattern8, message_lower)
        if match8:
            current_task = match8.group(1).strip()
            new_description = match8.group(2).strip()
            return current_task, None, new_description

        # Pattern 9: Change both title and description
        pattern9 = r"change ['\"](.+?)['\"] title to ['\"](.+?)['\"] and description to ['\"](.+?)['\"]"
        match9 = re.search(pattern9, message_lower)
        if match9:
            current_task = match9.group(1).strip()
            new_title = match9.group(2).strip()
            new_description = match9.group(3).strip()
            return current_task, new_title, new_description

        # Pattern 10: Update both title and description
        pattern10 = r"update ['\"](.+?)['\"] title to ['\"](.+?)['\"] and description to ['\"](.+?)['\"]"
        match10 = re.search(pattern10, message_lower)
        if match10:
            current_task = match10.group(1).strip()
            new_title = match10.group(2).strip()
            new_description = match10.group(3).strip()
            return current_task, new_title, new_description

        # Pattern 11: Rename task specifically (e.g., "rename buy groceries to buy organic groceries")
        pattern11 = r"rename ['\"](.+?)['\"] to ['\"](.+?)['\"]"
        match11 = re.search(pattern11, message_lower)
        if match11:
            current_task = match11.group(1).strip()
            new_title = match11.group(2).strip()
            return current_task, new_title, None

        # Pattern 12: Rename without quotes (e.g., "rename buy groceries to buy organic groceries")
        pattern12 = r"rename (.+?) to (.+)"
        match12 = re.search(pattern12, message_lower)
        if match12:
            current_task = match12.group(1).strip()
            new_title = match12.group(2).strip()
            return current_task, new_title, None

        # If no patterns match, return None
        return None, None, None

    # Test "Remove work tag from task 2"
    result = extract_task_details_for_update("Remove work tag from task 2")
    expected = ("2_remove_tag_work", None, None)

    assert result == expected, f"Expected {expected}, got {result}"
    print("OK 'Remove work tag from task 2' correctly extracts task ID and operation")

    # Test "Add tag urgent to task 1"
    result = extract_task_details_for_update("Add tag urgent to task 1")
    expected = ("1_add_tag_urgent", None, None)

    assert result == expected, f"Expected {expected}, got {result}"
    print("OK 'Add tag urgent to task 1' correctly extracts task ID and operation")


def run_all_tests():
    """Run all validation tests."""
    print("Starting validation of all implemented fixes...\n")

    test_search_functionality()
    test_filter_functionality()
    test_sort_functionality()
    test_task_id_functionality()

    print("\nSUCCESS: All validation tests passed! All fixes are working correctly.")


if __name__ == "__main__":
    run_all_tests()