#!/usr/bin/env python3
"""
More specific debug to test the exact scenario
"""
import os
import sys

# Add backend/src to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from src.services.agent import extract_task_title


def test_extract_task_title():
    """Test the extract_task_title function with specific examples"""
    print("Testing extract_task_title function...")

    test_cases = [
        "add groceries",
        "Add task to buy groceries",
        "add a task to buy milk",
        "create task buy bread",
        "need to call mom",
        "remember to water plants",
        "should clean room"
    ]

    for case in test_cases:
        result = extract_task_title(case)
        print(f"Input: '{case}' -> Output: '{result}'")

        # Test the prefix matching logic manually
        message = case.strip()
        prefixes = [
            "add task to ",
            "add a task to ",
            "create task to ",
            "create a task to ",
            "add task ",
            "add ",
            "create task ",
            "create ",
            "new task ",
            "remember to ",
            "need to ",
            "have to ",
            "should "
        ]

        matched_prefix = None
        for prefix in prefixes:
            if message.lower().startswith(prefix):
                matched_prefix = prefix
                break

        print(f"  Matched prefix: '{matched_prefix}'")
        if matched_prefix:
            expected = message[len(matched_prefix):].strip()
            print(f"  Expected output: '{expected}'")
        print()


if __name__ == "__main__":
    test_extract_task_title()