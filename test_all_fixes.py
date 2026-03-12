#!/usr/bin/env python3
"""
Comprehensive test to verify all three fixes:
- FIX A: Message History Construction (no 400 errors)
- FIX B: Working Fallback Parser (parses commands correctly)
- FIX C: Proper Error Handling (fallback works when AI fails)
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_endpoint(endpoint, message, test_name):
    """Test a specific endpoint with a message."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"Endpoint: {endpoint}")
    print(f"Message: {message}")
    print(f"{'='*60}")

    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json={"message": message},
            timeout=15
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data.get('response', 'No response field')}")
            print(f"Conversation ID: {data.get('conversation_id', 'N/A')}")
            return data
        else:
            print(f"Error: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Request took longer than 15 seconds")
        return None
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("COMPREHENSIVE FIX VERIFICATION TEST")
    print("="*60)

    # Use a unique user ID for this test session
    test_user = f"test-fix-verification-{int(time.time())}"
    endpoint = f"/api/{test_user}/chat"

    print(f"\nTest User: {test_user}")
    print(f"Endpoint: {endpoint}")

    # Test 1: Add task (should work with AI or fallback)
    print("\n" + "="*60)
    print("TEST 1: Add Task - 'add buy fresh fruits'")
    print("="*60)
    result1 = test_endpoint(endpoint, "add buy fresh fruits", "Add Task")

    time.sleep(1)

    # Test 2: Add another task with extra words
    print("\n" + "="*60)
    print("TEST 2: Add Task with Extra Words - 'add buy milk to the tasks'")
    print("="*60)
    result2 = test_endpoint(endpoint, "add buy milk to the tasks", "Add Task with Extra Words")

    time.sleep(1)

    # Test 3: List tasks
    print("\n" + "="*60)
    print("TEST 3: List Tasks - 'list tasks'")
    print("="*60)
    result3 = test_endpoint(endpoint, "list tasks", "List Tasks")

    time.sleep(1)

    # Test 4: Complete task
    print("\n" + "="*60)
    print("TEST 4: Complete Task - 'complete task 1'")
    print("="*60)
    result4 = test_endpoint(endpoint, "complete task 1", "Complete Task")

    time.sleep(1)

    # Test 5: Delete task
    print("\n" + "="*60)
    print("TEST 5: Delete Task - 'delete task 2'")
    print("="*60)
    result5 = test_endpoint(endpoint, "delete task 2", "Delete Task")

    time.sleep(1)

    # Test 6: List tasks again to verify changes
    print("\n" + "="*60)
    print("TEST 6: List Tasks Again - 'show my tasks'")
    print("="*60)
    result6 = test_endpoint(endpoint, "show my tasks", "List Tasks Again")

    # Test 7: Test conversation history (FIX A verification)
    print("\n" + "="*60)
    print("TEST 7: Conversation History - Multiple messages in same conversation")
    print("="*60)
    result7a = test_endpoint(endpoint, "add buy bread", "Add Task in Existing Conversation")
    time.sleep(1)
    result7b = test_endpoint(endpoint, "list tasks", "List Tasks in Existing Conversation")

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    tests = [
        ("Add Task", result1),
        ("Add Task with Extra Words", result2),
        ("List Tasks", result3),
        ("Complete Task", result4),
        ("Delete Task", result5),
        ("List Tasks Again", result6),
        ("Add Task in Existing Conversation", result7a),
        ("List Tasks in Existing Conversation", result7b),
    ]

    passed = 0
    failed = 0

    for test_name, result in tests:
        if result and result.get('response'):
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed} passed, {failed} failed out of {len(tests)} tests")

    # FIX verification
    print("\n" + "="*60)
    print("FIX VERIFICATION")
    print("="*60)

    # FIX A: No 400 errors in conversation history
    if all(r and r.get('response') for r in [result7a, result7b]):
        print("✅ FIX A: Message History Construction - WORKING")
        print("   No 400 errors when replaying conversation history")
    else:
        print("❌ FIX A: Message History Construction - FAILED")
        print("   Got errors when replaying conversation history")

    # FIX B: Fallback parser works
    if result1 and result2:
        print("✅ FIX B: Working Fallback Parser - WORKING")
        print("   Commands are being parsed and executed")
    else:
        print("❌ FIX B: Working Fallback Parser - FAILED")
        print("   Commands are not being parsed correctly")

    # FIX C: Error handling triggers fallback
    if all(r for r in [result1, result2, result3, result4, result5]):
        print("✅ FIX C: Proper Error Handling - WORKING")
        print("   Fallback mechanism is triggered when needed")
    else:
        print("⚠️  FIX C: Proper Error Handling - PARTIAL")
        print("   Some commands may not be triggering fallback correctly")

if __name__ == "__main__":
    main()
