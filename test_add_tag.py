#!/usr/bin/env python3
"""
Quick test for the "Add tag shopping" case
"""
import sys
import os

# Add backend src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from backend.src.services.agent import extract_task_details_with_priority_and_tags


def test_add_tag_shopping():
    """Test the 'Add tag shopping' case"""
    print("Testing 'Add tag shopping'...")
    title, priority, tags = extract_task_details_with_priority_and_tags("Add tag shopping")
    print(f"  Title: '{title}', Priority: '{priority}', Tags: {tags}")

    print("\nTesting 'Add shopping task'...")
    title2, priority2, tags2 = extract_task_details_with_priority_and_tags("Add shopping task")
    print(f"  Title: '{title2}', Priority: '{priority2}', Tags: {tags2}")


if __name__ == "__main__":
    test_add_tag_shopping()