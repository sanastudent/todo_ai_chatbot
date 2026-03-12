#!/usr/bin/env python3
"""
Test the actual function to see what's happening
"""
import sys
import os

# Add backend src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from backend.src.services.agent import extract_task_details_with_priority_and_tags


def test_actual_function():
    """Test the actual function"""
    message = "Add tag shopping"
    print(f"Testing: '{message}'")

    title, priority, tags = extract_task_details_with_priority_and_tags(message)
    print(f"Result -> Title: '{title}', Priority: '{priority}', Tags: {tags}")

    # Test the special case for "Add tag shopping" - should have title = "shopping"
    if not title and tags and "add tag " in message.lower():
        print("Special case should apply: title is empty but tags exist and message contains 'add tag'")
        print(f"Using first tag as title: {tags[0]}")
    else:
        print("Special case did not apply")


if __name__ == "__main__":
    test_actual_function()