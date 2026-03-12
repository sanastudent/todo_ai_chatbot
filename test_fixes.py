#!/usr/bin/env python3
"""
Test script to verify the fixes for inconsistent task matching in the Todo AI Chatbot
"""

import re

# Import the functions we need to test from the agent file
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from backend.src.services.agent import (
    extract_task_title_to_complete,
    extract_task_details_for_update,
    extract_task_title_to_delete
)

def test_extract_task_title_to_complete():
    """Test the extract_task_title_to_complete function"""
    print("Testing extract_task_title_to_complete function:")

    test_cases = [
        ("Complete task 1", "1"),
        ("Mark task 1 as complete", "1"),
        ("Finish task 2", "2"),
        ("Complete task #3", "3"),
        ("Mark task number 4 as complete", "4"),
        ("Complete buy groceries", "buy groceries"),
        ("Finish the project", "the project"),
        ("Mark task as complete", "task as complete"),  # edge case
    ]

    for input_msg, expected in test_cases:
        result = extract_task_title_to_complete(input_msg)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{input_msg}' -> '{result}' (expected: '{expected}')")

    print()

def test_extract_task_details_for_update():
    """Test the extract_task_details_for_update function"""
    print("Testing extract_task_details_for_update function:")

    test_cases = [
        ("Update task 1 to buy organic groceries", ("1", "buy organic groceries", None)),
        ("Change task 2 to walk the dog", ("2", "walk the dog", None)),
        ("Update 'buy groceries' to 'buy organic groceries'", ("buy groceries", "buy organic groceries", None)),
        ("Change 'walk the dog' to 'walk the cat'", ("walk the dog", "walk the cat", None)),
        ("Modify task 3 to call mom", ("3", "call mom", None)),
        ("Update task 5", (None, None, None)),  # No match case
    ]

    for input_msg, expected in test_cases:
        result = extract_task_details_for_update(input_msg)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{input_msg}' -> {result} (expected: {expected})")

    print()

def test_extract_task_title_to_delete():
    """Test the extract_task_title_to_delete function"""
    print("Testing extract_task_title_to_delete function:")

    test_cases = [
        ("Delete task 1", "1"),
        ("Remove task 2", "2"),
        ("Cancel task 3", "3"),
        ("Delete task #4", "4"),
        ("Remove task number 5", "5"),
        ("Delete buy groceries", "buy groceries"),
        ("Remove the project", "the project"),
    ]

    for input_msg, expected in test_cases:
        result = extract_task_title_to_delete(input_msg)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{input_msg}' -> '{result}' (expected: '{expected}')")

    print()

def test_regex_patterns():
    """Test the regex patterns directly"""
    print("Testing regex patterns directly:")

    # Test numbered completion patterns
    completion_patterns = [
        r'(?:complete|finish|done|mark as complete|mark)\s+(?:task\s+)?(?:number\s+|#)?(\d+)(?:\s+as\s+complete)?',
        r'(?:complete|finish|done|mark as complete|mark)\s+(?:the\s+|a\s+|an\s+)?task\s+(\d+)',
        r'(?:complete|finish|done|mark as complete|mark)\s+(\d+)(?:\s+as\s+complete)?'
    ]

    completion_tests = [
        ("Complete task 1", "1"),
        ("Mark task 1 as complete", "1"),
        ("Finish task 2", "2"),
        ("Complete 3", "3"),
        ("Mark 4 as complete", "4"),
    ]

    for pattern in completion_patterns:
        print(f"  Pattern: {pattern}")
        for test_input, expected in completion_tests:
            match = re.search(pattern, test_input.lower())
            if match:
                result = match.group(1)
                status = "✅" if result == expected else "❌"
                print(f"    {status} '{test_input}' -> '{result}' (expected: '{expected}')")
            else:
                print(f"    ❌ '{test_input}' -> no match (expected: '{expected}')")

    print()

if __name__ == "__main__":
    print("Testing fixes for inconsistent task matching in Todo AI Chatbot")
    print("=" * 70)

    test_regex_patterns()
    test_extract_task_title_to_complete()
    test_extract_task_details_for_update()
    test_extract_task_title_to_delete()

    print("All tests completed!")