#!/usr/bin/env python3
"""
Debug tag extraction only
"""
import re

def test_tag_extraction():
    """Test just the tag extraction logic"""
    message = "Create task with tags work and urgent"
    message_lower = message.lower()

    print(f"Original message: '{message}'")
    print(f"Lowercase: '{message_lower}'")

    # Test tag pattern
    pattern = r'with tags ([^,.]+)'
    match = re.search(pattern, message_lower)
    if match:
        print(f"Pattern '{pattern}' matched!")
        tag_text = match.group(1).strip()
        print(f"Captured: '{tag_text}'")

        # Split tags by commas, semicolons, or ' and ' (with spaces around 'and')
        raw_tags = re.split(r'[,\s]+|;\s*|\s+and\s+', tag_text)
        print(f"After splitting: {raw_tags}")

        tags = []
        for raw_tag in raw_tags:
            clean_tag = raw_tag.strip().lower()
            if clean_tag and clean_tag not in tags:
                tags.append(clean_tag)

        print(f"Clean tags: {tags}")
    else:
        print(f"Pattern '{pattern}' did not match!")


if __name__ == "__main__":
    test_tag_extraction()