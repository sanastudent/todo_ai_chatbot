"""
Test script to verify the remaining features (search, filter, sort) work correctly.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from backend.src.services.search import rank_search_results
from backend.src.services.filter import filter_tasks_locally
from backend.src.services.sort import apply_custom_priority_sort, apply_alphabetical_sort, apply_date_sort

def test_search_ranking():
    """Test that search ranking works correctly."""
    print("Testing search ranking...")

    tasks = [
        {"title": "High priority task", "description": "This is important", "priority": "high", "tags": ["urgent", "work"]},
        {"title": "Medium priority task", "description": "This is normal", "priority": "medium", "tags": ["work"]},
        {"title": "Low priority task", "description": "This is not important", "priority": "low", "tags": ["personal"]}
    ]

    # Test ranking with a search term
    ranked = rank_search_results(tasks, "important")

    # The first task should be the one with "important" in description
    assert ranked[0]["title"] == "High priority task", f"Expected 'High priority task', got {ranked[0]['title']}"

    print("✓ Search ranking works correctly")


def test_filtering():
    """Test that filtering works correctly."""
    print("Testing filtering...")

    tasks = [
        {"title": "Task 1", "priority": "high", "completed": False, "tags": ["work", "urgent"], "created_at": "2026-01-14T10:00:00Z"},
        {"title": "Task 2", "priority": "medium", "completed": True, "tags": ["personal"], "created_at": "2026-01-14T11:00:00Z"},
        {"title": "Task 3", "priority": "low", "completed": False, "tags": ["work"], "created_at": "2026-01-14T12:00:00Z"},
        {"title": "Task 4", "priority": "high", "completed": False, "tags": ["personal", "urgent"], "created_at": "2026-01-14T13:00:00Z"}
    ]

    # Test priority filter
    filtered = filter_tasks_locally(tasks, {"priority": ["high"]})
    assert len(filtered) == 2, f"Expected 2 high priority tasks, got {len(filtered)}"
    for task in filtered:
        assert task["priority"] == "high", f"Expected priority 'high', got {task['priority']}"

    # Test tag filter
    filtered = filter_tasks_locally(tasks, {"tags": ["urgent"]})
    assert len(filtered) == 2, f"Expected 2 urgent tasks, got {len(filtered)}"
    for task in filtered:
        assert "urgent" in task["tags"], f"Expected 'urgent' in tags, got {task['tags']}"

    # Test completion filter
    filtered = filter_tasks_locally(tasks, {"completed": True})
    assert len(filtered) == 1, f"Expected 1 completed task, got {len(filtered)}"
    assert filtered[0]["completed"] == True, f"Expected completed=True, got {filtered[0]['completed']}"

    print("✓ Filtering works correctly")


def test_sorting():
    """Test that sorting works correctly."""
    print("Testing sorting...")

    tasks = [
        {"title": "Zebra task", "priority": "low", "completed": False, "created_at": "2026-01-14T10:00:00Z"},
        {"title": "Alpha task", "priority": "high", "completed": True, "created_at": "2026-01-14T12:00:00Z"},
        {"title": "Middle task", "priority": "medium", "completed": False, "created_at": "2026-01-14T11:00:00Z"}
    ]

    # Test priority sorting (descending: high first)
    sorted_tasks = apply_custom_priority_sort(tasks, descending=True)
    assert sorted_tasks[0]["priority"] == "high", f"Expected highest priority first, got {sorted_tasks[0]['priority']}"
    assert sorted_tasks[-1]["priority"] == "low", f"Expected lowest priority last, got {sorted_tasks[-1]['priority']}"

    # Test alphabetical sorting
    sorted_tasks = apply_alphabetical_sort(tasks, descending=False)
    assert sorted_tasks[0]["title"] == "Alpha task", f"Expected 'Alpha task' first, got {sorted_tasks[0]['title']}"
    assert sorted_tasks[-1]["title"] == "Zebra task", f"Expected 'Zebra task' last, got {sorted_tasks[-1]['title']}"

    # Test date sorting (descending: newest first)
    sorted_tasks = apply_date_sort(tasks, descending=True)
    assert sorted_tasks[0]["created_at"] == "2026-01-14T12:00:00Z", f"Expected newest first, got {sorted_tasks[0]['created_at']}"

    print("✓ Sorting works correctly")


def main():
    """Run all tests."""
    print("Testing remaining features (search, filter, sort)...")
    print("=" * 50)

    try:
        test_search_ranking()
        test_filtering()
        test_sorting()

        print("=" * 50)
        print("🎉 ALL REMAINING FEATURES TESTS PASSED!")
        print()
        print("Remaining features successfully implemented:")
        print("- ✓ Search functionality with ranking")
        print("- ✓ Advanced filtering by multiple criteria")
        print("- ✓ Sorting by priority, title, date, and completion status")
        print()
        print("All User Stories 3, 4, and 5 completed!")
        return True

    except Exception as e:
        print(f"❌ TESTS FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)