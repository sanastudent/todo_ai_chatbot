#!/usr/bin/env python3
"""
Simple MCP Tools Verification Test
Avoids Unicode encoding issues by checking response content without printing emojis
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8001/api"
test_user = f"simple-test-{int(time.time())}"

def test_command(message, expected_indicators, test_name):
    """Test a command and verify response indicators"""
    endpoint = f"{BASE_URL}/{test_user}/chat"

    try:
        print(f"\n[TEST] {test_name}")
        print(f"  Input: '{message}'")

        response = requests.post(endpoint, json={"message": message}, timeout=20)

        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '').lower()

            # Check for failure indicators
            if "couldn't understand" in response_text:
                print(f"  Result: FAIL - Got 'couldn't understand' message")
                print(f"  Response preview: {response_text[:100]}")
                return False

            if "ai natural language processing is not available" in response_text:
                print(f"  Result: FAIL - AI not available message")
                return False

            # Check for expected indicators
            found_indicators = []
            missing_indicators = []

            for indicator in expected_indicators:
                if indicator.lower() in response_text:
                    found_indicators.append(indicator)
                else:
                    missing_indicators.append(indicator)

            if missing_indicators:
                print(f"  Result: FAIL - Missing indicators: {missing_indicators}")
                print(f"  Found: {found_indicators}")
                # Print response without emojis
                clean_response = response_text.encode('ascii', 'ignore').decode('ascii')
                print(f"  Response preview: {clean_response[:150]}")
                return False

            print(f"  Result: PASS - All indicators found: {found_indicators}")
            return True

        else:
            print(f"  Result: FAIL - HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"  Result: FAIL - Error: {str(e)}")
        return False

def main():
    print("="*70)
    print("SIMPLE MCP TOOLS VERIFICATION TEST")
    print("="*70)
    print(f"Test User: {test_user}")
    print(f"Backend: {BASE_URL}")

    # Check backend
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("\n[OK] Backend is running")
        else:
            print(f"\n[FAIL] Backend returned {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] Backend not accessible: {str(e)}")
        sys.exit(1)

    # Run tests
    results = []

    print("\n" + "="*70)
    print("RUNNING TESTS")
    print("="*70)

    # Test 1: Add task
    results.append(test_command(
        "add buy fresh fruits to the tasks",
        ['task', 'added', 'fresh fruits'],
        "Add Task"
    ))
    time.sleep(1)

    # Test 2: List tasks
    results.append(test_command(
        "list all the tasks",
        ['tasks', 'fresh fruits'],
        "List Tasks"
    ))
    time.sleep(1)

    # Test 3: Complete task
    results.append(test_command(
        "complete task number 1",
        ['completed', 'fresh fruits'],
        "Complete Task"
    ))
    time.sleep(1)

    # Test 4: Add another task
    results.append(test_command(
        "add task to delete later",
        ['task', 'added'],
        "Add Task 2"
    ))
    time.sleep(1)

    # Test 5: Natural language variation
    results.append(test_command(
        "Add a task to buy groceries",
        ['task', 'added', 'groceries'],
        "Natural Language Add"
    ))
    time.sleep(1)

    # Test 6: Natural language list
    results.append(test_command(
        "Show me all my tasks",
        ['tasks'],
        "Natural Language List"
    ))
    time.sleep(1)

    # Test 7: Natural language add variation
    results.append(test_command(
        "I need to remember to pay bills",
        ['task', 'added', 'bills'],
        "Natural Language Add 2"
    ))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(results)
    failed = len(results) - passed
    success_rate = (passed / len(results) * 100) if results else 0

    print(f"\nTotal Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {success_rate:.1f}%")

    if failed == 0:
        print("\n[SUCCESS] All tests passed! MCP tools are working correctly.")
        sys.exit(0)
    elif success_rate >= 70:
        print("\n[PARTIAL] Most tests passed, but some issues remain.")
        sys.exit(1)
    else:
        print("\n[FAILURE] System has significant issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()
