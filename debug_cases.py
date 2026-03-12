#!/usr/bin/env python3
"""
Debug specific cases that are failing
"""
import sys
import os

# Add backend src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from backend.src.services.agent import extract_task_details_with_priority_and_tags


def debug_cases():
    """Debug the failing cases"""

    print("Testing 'Create task with tags work and urgent':")
    title, priority, tags = extract_task_details_with_priority_and_tags("Create task with tags work and urgent")
    print(f"  Title: '{title}', Priority: '{priority}', Tags: {tags}")

    print("\nTesting 'Add a high priority task to buy groceries':")
    title, priority, tags = extract_task_details_with_priority_and_tags("Add a high priority task to buy groceries")
    print(f"  Title: '{title}', Priority: '{priority}', Tags: {tags}")


if __name__ == "__main__":
    debug_cases()