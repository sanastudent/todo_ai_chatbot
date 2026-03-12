#!/usr/bin/env python3
"""
Simple test to verify that the pattern ordering fix works correctly.
This verifies that commands like "add work task: finish report with urgent tag"
are properly handled by the detailed pattern rather than the general add pattern.
"""

import re

def simulate_agent_logic(user_message):
    """Simulate the agent's pattern matching logic"""
    user_message = user_message.strip('"\' ').lower()

    print(f"Processing message: '{user_message}'")

    # DETAILED ADD PATTERNS (MUST BE CHECKED BEFORE GENERAL ADD):

    # NEW: Pattern for "add [category] task: [title] with [tag] tag" → add_task_with_details
    detailed_add_match_colon = re.search(r'^add\s+(\w+)\s+task:\s+(.+)$', user_message.strip())
    if detailed_add_match_colon:
        print("[OK] Matched detailed pattern: 'add [category] task: [title]'")
        category = detailed_add_match_colon.group(1).strip()
        title_with_possible_tags = detailed_add_match_colon.group(2).strip()

        title = title_with_possible_tags
        tags = []

        # Extract tags from the title part
        tag_pattern = r'with\s+(.+?)\s+tag(?:s?)'
        tag_match = re.search(tag_pattern, title.lower())
        if tag_match:
            tag_part = tag_match.group(1).strip()
            # Split tags by 'and' or commas
            raw_tags = re.split(r'\s+and\s+|\s*,\s*', tag_part)
            for raw_tag in raw_tags:
                clean_tag = raw_tag.strip()
                if clean_tag and clean_tag not in tags:
                    tags.append(clean_tag)

            # Remove the tag part from the title
            title = re.sub(tag_pattern, '', title, flags=re.IGNORECASE).strip()
            title = re.sub(r'\s+', ' ', title).strip()  # Clean up extra spaces

        # Validate that the category is a common category
        common_categories = ['work', 'personal', 'shopping', 'urgent', 'home', 'family']
        if category not in common_categories:
            print(f"[WARN] Category '{category}' not in common categories, falling through to general add")
            pass
        else:
            print(f"[OK] Processing with add_task_with_details:")
            print(f"  - Category: {category}")
            print(f"  - Title: {title}")
            print(f"  - Tags: {tags}")
            return "detailed_add"

    # GENERAL ADD PATTERN (MUST BE LAST):
    # Pattern: add (.+) → add_task
    add_match = re.search(r'^add\s+(.+)$', user_message.strip())
    if add_match:
        print("[OK] Matched general pattern: 'add (.+)'")
        task_title = add_match.group(1).strip()
        print(f"  - Title: {task_title}")
        return "general_add"

    print("[ERROR] No pattern matched")
    return "no_match"

# Test cases
test_cases = [
    "add work task: finish report with urgent tag",
    "add personal task: buy groceries with shopping and weekly tags",
    "add task to buy milk",  # Should use general add
    "add meeting notes",     # Should use general add
    "add urgent task: fix bug with high priority tag"  # Should use detailed add
]

print("Testing pattern matching logic:")
print("=" * 60)

for test_case in test_cases:
    print(f"\nTest: {test_case}")
    result = simulate_agent_logic(test_case)
    print(f"Result: {result}")
    print("-" * 40)

print("\nExpected results:")
print("- 'add work task: finish report with urgent tag' → Should use detailed_add with category='work', title='finish report', tags=['urgent']")
print("- 'add personal task: buy groceries with shopping and weekly tags' → Should use detailed_add with category='personal', title='buy groceries', tags=['shopping', 'weekly']")
print("- Other general add commands → Should use general_add")