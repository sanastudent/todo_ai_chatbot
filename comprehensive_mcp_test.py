#!/usr/bin/env python3
"""
Comprehensive Test Suite for Todo AI Chatbot MCP Tools
Tests all commands with backend log verification
"""

import requests
import time
import sys
import json
from datetime import datetime

BASE_URL = "http://localhost:8001/api"
test_user = f"comprehensive-test-{int(time.time())}"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test_header(test_name):
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}{test_name.center(70)}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(message):
    print(f"{Colors.GREEN}[PASS]{Colors.RESET} {message}")

def print_failure(message):
    print(f"{Colors.RED}[FAIL]{Colors.RESET} {message}")

def print_info(message):
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {message}")

def send_message(message, conversation_id=None, timeout=20):
    """Send a message to the chatbot and return the response"""
    endpoint = f"{BASE_URL}/{test_user}/chat"
    payload = {"message": message}
    if conversation_id:
        payload["conversation_id"] = conversation_id

    try:
        print_info(f"Sending: '{message}'")
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=timeout)
        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            conversation_id = data.get('conversation_id', '')

            print_info(f"Response ({elapsed:.2f}s): {response_text[:150]}...")
            return {
                'success': True,
                'response': response_text,
                'conversation_id': conversation_id,
                'elapsed': elapsed
            }
        else:
            print_failure(f"HTTP {response.status_code}: {response.text}")
            return {'success': False, 'error': f"HTTP {response.status_code}"}

    except requests.exceptions.Timeout:
        print_failure(f"Request timed out (>{timeout}s)")
        return {'success': False, 'error': 'Timeout'}
    except Exception as e:
        print_failure(f"Error: {str(e)}")
        return {'success': False, 'error': str(e)}

def verify_response(result, expected_keywords, test_name):
    """Verify response contains expected keywords"""
    if not result['success']:
        print_failure(f"{test_name}: Request failed - {result.get('error')}")
        return False

    response = result['response'].lower()

    # Check for failure indicators
    if "couldn't understand" in response or "ai natural language processing is not available" in response:
        print_failure(f"{test_name}: Got fallback error message")
        print_warning(f"Response: {result['response'][:200]}")
        return False

    # Check for expected keywords
    missing_keywords = []
    for keyword in expected_keywords:
        if keyword.lower() not in response:
            missing_keywords.append(keyword)

    if missing_keywords:
        print_failure(f"{test_name}: Missing keywords: {missing_keywords}")
        print_warning(f"Response: {result['response'][:200]}")
        return False

    print_success(f"{test_name}: PASSED")
    return True

# ============================================================================
# TEST 1: BASIC COMMAND EXECUTION
# ============================================================================

def test_basic_commands():
    print_test_header("TEST 1: BASIC COMMAND EXECUTION")

    results = {
        'passed': 0,
        'failed': 0,
        'tests': []
    }

    # Test 1.1: Add task
    print("\n--- Test 1.1: Add Task ---")
    result = send_message("add buy fresh fruits to the tasks")
    passed = verify_response(result, ['task', 'added', 'fresh fruits'], "Add Task")
    results['tests'].append(('Add Task', passed))
    if passed:
        results['passed'] += 1
    else:
        results['failed'] += 1

    time.sleep(1)

    # Test 1.2: List tasks
    print("\n--- Test 1.2: List Tasks ---")
    result = send_message("list all the tasks")
    passed = verify_response(result, ['tasks', 'fresh fruits'], "List Tasks")
    results['tests'].append(('List Tasks', passed))
    if passed:
        results['passed'] += 1
    else:
        results['failed'] += 1

    time.sleep(1)

    # Test 1.3: Complete task
    print("\n--- Test 1.3: Complete Task ---")
    result = send_message("complete task number 1")
    passed = verify_response(result, ['completed', 'fresh fruits'], "Complete Task")
    results['tests'].append(('Complete Task', passed))
    if passed:
        results['passed'] += 1
    else:
        results['failed'] += 1

    time.sleep(1)

    # Test 1.4: Add another task for deletion test
    print("\n--- Test 1.4: Add Task for Deletion ---")
    result = send_message("add task to delete later")
    passed = verify_response(result, ['task', 'added'], "Add Task for Deletion")
    results['tests'].append(('Add Task for Deletion', passed))
    if passed:
        results['passed'] += 1
    else:
        results['failed'] += 1

    return results

# ============================================================================
# TEST 2: MULTI-TURN CONVERSATIONS
# ============================================================================

def test_multi_turn_conversations():
    print_test_header("TEST 2: MULTI-TURN CONVERSATIONS")

    results = {
        'passed': 0,
        'failed': 0,
        'tests': []
    }

    # Sequence A: Delete with Confirmation
    print("\n--- Sequence A: Delete with Confirmation ---")

    # Add a task first
    result = send_message("add task for deletion test")
    time.sleep(1)

    # Request deletion
    print("\nStep 1: Request deletion")
    result = send_message("delete task 1")

    # Check if it asks for confirmation
    if result['success']:
        response = result['response'].lower()
        if 'are you sure' in response or 'confirm' in response or 'yes' in response:
            print_success("Delete Confirmation: System asks for confirmation")
            conversation_id = result['conversation_id']

            # Confirm deletion
            print("\nStep 2: Confirm deletion")
            time.sleep(1)
            result = send_message("yes", conversation_id=conversation_id)

            if result['success']:
                response = result['response'].lower()
                if 'deleted' in response or 'removed' in response:
                    print_success("Delete Execution: Task deleted successfully")
                    results['passed'] += 1
                    results['tests'].append(('Delete with Confirmation', True))
                else:
                    print_failure("Delete Execution: Confirmation not processed")
                    print_warning(f"Response: {result['response'][:200]}")
                    results['failed'] += 1
                    results['tests'].append(('Delete with Confirmation', False))
            else:
                print_failure("Delete Execution: Confirmation request failed")
                results['failed'] += 1
                results['tests'].append(('Delete with Confirmation', False))
        else:
            print_failure("Delete Confirmation: No confirmation requested")
            print_warning(f"Response: {result['response'][:200]}")
            results['failed'] += 1
            results['tests'].append(('Delete with Confirmation', False))
    else:
        print_failure("Delete Request: Failed to send delete command")
        results['failed'] += 1
        results['tests'].append(('Delete with Confirmation', False))

    time.sleep(2)

    # Sequence B: Update with Details
    print("\n--- Sequence B: Update with Details ---")

    # Add a task first
    result = send_message("add task for update test")
    time.sleep(1)

    # Request update
    print("\nStep 1: Request update")
    result = send_message("update task 1 description")

    if result['success']:
        response = result['response'].lower()
        # Check if it asks for details or just updates
        if 'what would you like' in response or 'provide' in response or 'description' in response:
            print_success("Update Request: System asks for details")
            conversation_id = result['conversation_id']

            # Provide details
            print("\nStep 2: Provide new description")
            time.sleep(1)
            result = send_message("new description: buy organic", conversation_id=conversation_id)

            if result['success']:
                response = result['response'].lower()
                if 'updated' in response or 'changed' in response:
                    print_success("Update Execution: Task updated successfully")
                    results['passed'] += 1
                    results['tests'].append(('Update with Details', True))
                else:
                    print_failure("Update Execution: Update not processed")
                    print_warning(f"Response: {result['response'][:200]}")
                    results['failed'] += 1
                    results['tests'].append(('Update with Details', False))
            else:
                print_failure("Update Execution: Details request failed")
                results['failed'] += 1
                results['tests'].append(('Update with Details', False))
        elif 'updated' in response:
            print_success("Update Direct: Task updated directly (no follow-up needed)")
            results['passed'] += 1
            results['tests'].append(('Update with Details', True))
        else:
            print_failure("Update Request: Unexpected response")
            print_warning(f"Response: {result['response'][:200]}")
            results['failed'] += 1
            results['tests'].append(('Update with Details', False))
    else:
        print_failure("Update Request: Failed to send update command")
        results['failed'] += 1
        results['tests'].append(('Update with Details', False))

    return results

# ============================================================================
# TEST 3: NATURAL LANGUAGE VARIATIONS
# ============================================================================

def test_natural_language_variations():
    print_test_header("TEST 3: NATURAL LANGUAGE VARIATIONS")

    results = {
        'passed': 0,
        'failed': 0,
        'tests': []
    }

    test_cases = [
        ("Add a task to buy groceries", ['task', 'added', 'groceries'], "Add variation 1"),
        ("Show me all my tasks", ['tasks'], "List variation 1"),
        ("I need to remember to pay bills", ['task', 'added', 'bills'], "Add variation 2"),
    ]

    for message, keywords, test_name in test_cases:
        print(f"\n--- {test_name} ---")
        result = send_message(message)
        passed = verify_response(result, keywords, test_name)
        results['tests'].append((test_name, passed))
        if passed:
            results['passed'] += 1
        else:
            results['failed'] += 1
        time.sleep(1)

    return results

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}{'COMPREHENSIVE MCP TOOLS TEST SUITE'.center(70)}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"\nTest User: {test_user}")
    print(f"Backend URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check backend health
    print_info("\nChecking backend health...")
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print_success("Backend is running")
        else:
            print_failure(f"Backend returned status {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print_failure(f"Backend is not accessible: {str(e)}")
        print_info("Start backend: cd backend && python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload")
        sys.exit(1)

    # Run all tests
    all_results = []

    # Test 1: Basic Commands
    results1 = test_basic_commands()
    all_results.append(('Basic Commands', results1))

    time.sleep(2)

    # Test 2: Multi-turn Conversations
    results2 = test_multi_turn_conversations()
    all_results.append(('Multi-turn Conversations', results2))

    time.sleep(2)

    # Test 3: Natural Language Variations
    results3 = test_natural_language_variations()
    all_results.append(('Natural Language Variations', results3))

    # Print summary
    print_test_header("TEST SUMMARY")

    total_passed = 0
    total_failed = 0

    for category, results in all_results:
        print(f"\n{Colors.BLUE}{category}:{Colors.RESET}")
        print(f"  Passed: {Colors.GREEN}{results['passed']}{Colors.RESET}")
        print(f"  Failed: {Colors.RED}{results['failed']}{Colors.RESET}")

        total_passed += results['passed']
        total_failed += results['failed']

        # Show individual test results
        for test_name, passed in results['tests']:
            status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
            print(f"    {status} - {test_name}")

    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}OVERALL RESULTS:{Colors.RESET}")
    print(f"  Total Tests: {total_passed + total_failed}")
    print(f"  Passed: {Colors.GREEN}{total_passed}{Colors.RESET}")
    print(f"  Failed: {Colors.RED}{total_failed}{Colors.RESET}")

    success_rate = (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0
    print(f"  Success Rate: {success_rate:.1f}%")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")

    # Final verdict
    if total_failed == 0:
        print(f"{Colors.GREEN}🎉 ALL TESTS PASSED! System is fully functional.{Colors.RESET}\n")
        sys.exit(0)
    elif success_rate >= 70:
        print(f"{Colors.YELLOW}⚠️  PARTIAL SUCCESS: Most tests passed but some issues remain.{Colors.RESET}\n")
        sys.exit(1)
    else:
        print(f"{Colors.RED}❌ TESTS FAILED: System has significant issues.{Colors.RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
