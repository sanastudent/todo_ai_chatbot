"""
Final verification script to test the implemented enhancements.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.src.models.task import Task
from backend.src.utils.validation import validate_and_sanitize_priority, validate_and_sanitize_tags

def test_task_model():
    """Test that the Task model has been properly updated with priority and tags fields."""
    print("Testing Task model...")

    # Create a task with priority and tags
    task = Task(
        user_id="test_user",
        title="Test task",
        priority="high",
        tags=["work", "urgent"]
    )

    assert hasattr(task, 'priority'), "Task model should have priority field"
    assert hasattr(task, 'tags'), "Task model should have tags field"
    assert task.priority == "high", f"Expected priority 'high', got {task.priority}"
    assert "work" in task.tags, f"Expected 'work' in tags, got {task.tags}"
    assert "urgent" in task.tags, f"Expected 'urgent' in tags, got {task.tags}"

    print("✓ Task model has priority and tags fields")


def test_validation_utilities():
    """Test that validation utilities work correctly."""
    print("Testing validation utilities...")

    # Test priority validation
    is_valid, sanitized, error = validate_and_sanitize_priority("HIGH")
    assert is_valid, f"Priority 'HIGH' should be valid, got error: {error}"
    assert sanitized == "high", f"Expected 'high', got {sanitized}"

    is_valid, sanitized, error = validate_and_sanitize_priority("invalid")
    assert not is_valid, "Invalid priority should not be valid"

    # Test tags validation
    is_valid, sanitized, error = validate_and_sanitize_tags(["work", "personal"])
    assert is_valid, f"Valid tags should be valid, got error: {error}"
    assert "work" in sanitized, f"Expected 'work' in sanitized tags, got {sanitized}"
    assert "personal" in sanitized, f"Expected 'personal' in sanitized tags, got {sanitized}"

    # Test duplicate removal in tags
    is_valid, sanitized, error = validate_and_sanitize_tags(["work", "work", "personal"])
    assert is_valid, f"Tags with duplicates should be valid after sanitization, got error: {error}"
    assert len(sanitized) == 2, f"Expected 2 unique tags after deduplication, got {len(sanitized)}"

    print("✓ Validation utilities work correctly")


def test_migration_exists():
    """Test that the migration file exists."""
    print("Testing migration file exists...")

    migration_path = "backend/migrations/versions/002_add_priority_tags_columns.py"
    assert os.path.exists(migration_path), f"Migration file should exist at {migration_path}"

    with open(migration_path, 'r') as f:
        content = f.read()
        assert "priority" in content.lower(), "Migration should include priority column"
        assert "tags" in content.lower(), "Migration should include tags column"

    print("✓ Migration file exists and includes required columns")


def test_mcp_tools_updated():
    """Test that MCP tools have been updated."""
    print("Testing MCP tools updates...")

    from backend.src.mcp.tools import add_task, update_task, list_tasks

    # Check that add_task accepts priority and tags parameters
    import inspect
    sig = inspect.signature(add_task)
    params = list(sig.parameters.keys())
    assert 'priority' in params, f"add_task should accept priority parameter, got params: {params}"
    assert 'tags' in params, f"add_task should accept tags parameter, got params: {params}"

    # Check that update_task accepts priority and tags parameters
    sig = inspect.signature(update_task)
    params = list(sig.parameters.keys())
    assert 'priority' in params, f"update_task should accept priority parameter, got params: {params}"
    assert 'tags' in params, f"update_task should accept tags parameter, got params: {params}"

    # Check that list_tasks accepts filtering parameters
    sig = inspect.signature(list_tasks)
    params = list(sig.parameters.keys())
    assert 'priority' in params, f"list_tasks should accept priority parameter, got params: {params}"
    assert 'tags' in params, f"list_tasks should accept tags parameter, got params: {params}"
    assert 'search_term' in params, f"list_tasks should accept search_term parameter, got params: {params}"

    print("✓ MCP tools have been updated with new parameters")


def main():
    """Run all verification tests."""
    print("Starting final verification of Todo AI Chatbot enhancements...")
    print("=" * 60)

    try:
        test_task_model()
        test_validation_utilities()
        test_migration_exists()
        test_mcp_tools_updated()

        print("=" * 60)
        print("🎉 ALL VERIFICATION TESTS PASSED!")
        print()
        print("Implemented features:")
        print("- ✓ Task model enhanced with priority and tags fields")
        print("- ✓ Validation utilities for priority and tags")
        print("- ✓ Database migration for new columns")
        print("- ✓ MCP tools updated with new parameters:")
        print("  - add_task: priority, tags")
        print("  - update_task: priority, tags")
        print("  - list_tasks: priority, tags, search_term, and other filters")
        print()
        print("MVP scope successfully implemented!")
        return True

    except Exception as e:
        print(f"❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)