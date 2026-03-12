"""
Simple regex pattern validation test (ASCII only)
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
            ],
        },
        {
            "name": "Complete Task with Variations",
            "pattern": r'^complete(?: my)? task (\d+)(?: please)?[.!?]*\s*$',
            "should_match": [
                "complete task 1",
                "complete my task 1",
                "complete task 1 please",
                "complete my task 2 please",
            ],
        },
        {
            "name": "Finish Task with Variations",
            "pattern": r'^finish(?: my)? task (\d+)(?: please)?[.!?]*\s*$',
            "should_match": [
                "finish task 1",
                "finish my task 2",
                "finish task 3 please",
            ],
        },
        {
            "name": "Mark Task Done with Variations",
            "pattern": r'^mark(?: my)? task (\d+) (?:as )?done[.!?]*\s*$',
            "should_match": [
                "mark task 1 done",
                "mark my task 1 done",
                "mark task 1 as done",
                "mark my task 2 as done",
            ],
        },
        {
            "name": "Delete Task with Variations",
            "pattern": r'^delete(?: my)? task (\d+)(?: please)?[.!?]*\s*$',
            "should_match": [
                "delete task 3",
                "delete my task 3",
                "delete task 3 please",
            ],
        },
        {
            "name": "Remove Task with Variations",
            "pattern": r'^remove(?: my)? task (\d+)(?: please)?[.!?]*\s*$',
            "should_match": [
                "remove task 1",
                "remove my task 1",
                "remove task 2 please",
            ],
        },
        {
            "name": "Cancel Task with Variations",
            "pattern": r'^cancel(?: my)? task (\d+)(?: please)?[.!?]*\s*$',
            "should_match": [
                "cancel task 2",
                "cancel my task 2",
                "cancel task 1 please",
            ],
        }
    ]

    total_tests = 0
    passed_tests = 0

    for test_case in test_cases:
        print("\n" + "-" * 80)
        print(f"Testing: {test_case['name']}")
        print(f"Pattern: {test_case['pattern']}")
        print("-" * 80)

        # Test strings that should match
        print("\nShould MATCH:")
        for test_str in test_case['should_match']:
            total_tests += 1
            match = re.search(test_case['pattern'], test_str.lower())
            if match:
                passed_tests += 1
                groups_str = f" -> Groups: {match.groups()}" if match.groups() else ""
                print(f"  [PASS] '{test_str}'{groups_str}")
            else:
                print(f"  [FAIL] '{test_str}' -> no match")

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    print("=" * 80)

    if total_tests == passed_tests:
        print("\nAll regex patterns are working correctly!")
    else:
        print(f"\n{total_tests - passed_tests} test(s) failed")

    return total_tests == passed_tests


if __name__ == "__main__":
    print("\nStarting regex pattern validation...\n")
    success = test_pattern_matching()
    print("\nTest completed!\n")
    exit(0 if success else 1)
