"""
Simple regex pattern validation test
Tests that the new patterns match the expected commands
"""
import re


def test_pattern_matching():
    """Test regex pattern matching for the new patterns"""

    print("=" * 80)
    print("REGEX PATTERN VALIDATION TEST")
    print("=" * 80)

    # Define the patterns we added
    test_cases = [
        {
            "name": "List/Show Tasks Pattern",
            "pattern": r'^(?:show|list)(?: my)? tasks[.!?]*\s*$',
            "should_match": [
                "show tasks",
                "list tasks",
                "show my tasks",
                "list my tasks",
                "show tasks!",
                "list my tasks?"
            ],
            "should_not_match": [
                "show all tasks",  # This has a different pattern
                "show pending tasks",
                "list completed tasks"
            ]
        },
        {
            "name": "Complete Task with Variations",
            "pattern": r'^complete(?: my)? task (\d+)(?: please)?[.!?]*\s*$',
            "should_match": [
                "complete task 1",
                "complete my task 1",
                "complete task 1 please",
                "complete my task 2 please",
                "complete task 5!",
                "complete my task 3 please!"
            ],
            "should_not_match": [
                "complete task",  # Missing number
                "complete 1",  # Missing "task"
                "complete the task 1"  # Extra word
            ]
        },
        {
            "name": "Finish Task with Variations",
            "pattern": r'^finish(?: my)? task (\d+)(?: please)?[.!?]*\s*$',
            "should_match": [
                "finish task 1",
                "finish my task 2",
                "finish task 3 please",
                "finish my task 4 please!"
            ],
            "should_not_match": [
                "finish task",
                "finish 1"
            ]
        },
        {
            "name": "Mark Task Done with Variations",
            "pattern": r'^mark(?: my)? task (\d+) (?:as )?done[.!?]*\s*$',
            "should_match": [
                "mark task 1 done",
                "mark my task 1 done",
                "mark task 1 as done",
                "mark my task 2 as done!",
                "mark task 3 done?"
            ],
            "should_not_match": [
                "mark task done",
                "mark 1 done"
            ]
        },
        {
            "name": "Delete Task with Variations",
            "pattern": r'^delete(?: my)? task (\d+)(?: please)?[.!?]*\s*$',
            "should_match": [
                "delete task 3",
                "delete my task 3",
                "delete task 3 please",
                "delete my task 1 please!",
                "delete task 5?"
            ],
            "should_not_match": [
                "delete task",
                "delete 3",
                "delete the task 3"
            ]
        },
        {
            "name": "Remove Task with Variations",
            "pattern": r'^remove(?: my)? task (\d+)(?: please)?[.!?]*\s*$',
            "should_match": [
                "remove task 1",
                "remove my task 1",
                "remove task 2 please",
                "remove my task 3 please!"
            ],
            "should_not_match": [
                "remove task",
                "remove 1"
            ]
        },
        {
            "name": "Cancel Task with Variations",
            "pattern": r'^cancel(?: my)? task (\d+)(?: please)?[.!?]*\s*$',
            "should_match": [
                "cancel task 2",
                "cancel my task 2",
                "cancel task 1 please",
                "cancel my task 3 please!"
            ],
            "should_not_match": [
                "cancel task",
                "cancel 2"
            ]
        }
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for test_case in test_cases:
        print(f"\n{'─' * 80}")
        print(f"Testing: {test_case['name']}")
        print(f"Pattern: {test_case['pattern']}")
        print(f"{'─' * 80}")

        # Test strings that should match
        print("\n✓ Should MATCH:")
        for test_str in test_case['should_match']:
            total_tests += 1
            match = re.search(test_case['pattern'], test_str.lower())
            if match:
                passed_tests += 1
                groups_str = f" → Groups: {match.groups()}" if match.groups() else ""
                print(f"  ✅ '{test_str}'{groups_str}")
            else:
                failed_tests += 1
                print(f"  ❌ '{test_str}' → FAILED (no match)")

        # Test strings that should NOT match
        print("\n✗ Should NOT match:")
        for test_str in test_case['should_not_match']:
            total_tests += 1
            match = re.search(test_case['pattern'], test_str.lower())
            if not match:
                passed_tests += 1
                print(f"  ✅ '{test_str}' → Correctly rejected")
            else:
                failed_tests += 1
                print(f"  ❌ '{test_str}' → FAILED (should not match)")

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    print("=" * 80)

    if failed_tests == 0:
        print("\nAll regex patterns are working correctly!")
    else:
        print(f"\n{failed_tests} test(s) failed - patterns may need adjustment")

    return failed_tests == 0


if __name__ == "__main__":
    print("\nStarting regex pattern validation...\n")
    success = test_pattern_matching()
    print("\nTest completed!\n")
    exit(0 if success else 1)
