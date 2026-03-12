#!/usr/bin/env python3
"""
Debug script to understand how the current parsing works
"""
import sys
import os

# Add backend src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from backend.src.services.agent import extract_task_details_with_priority_and_tags


def debug_parsing():
    """Debug the parsing functions to understand current behavior"""
    print("Debugging command parsing...")

    test_cases = [
        "Add high priority task",
        "Add work task",
        "Add a work task",
        "Create task with tags work",
        "Add tag shopping",
        "Add urgent task",
        "Add task with tags work and urgent",
    ]

    for case in test_cases:
        print(f"\nTesting: '{case}'")
        title, priority, tags = extract_task_details_with_priority_and_tags(case)
        print(f"  Result -> Title: '{title}', Priority: '{priority}', Tags: {tags}")


if __name__ == "__main__":
    debug_parsing()