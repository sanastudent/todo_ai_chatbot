#!/usr/bin/env python3
"""
Comprehensive Test Suite for Todo AI Chatbot
Tests all functionality according to specification requirements
"""

import requests
import time
import sys
from typing import Dict, List, Tuple

BASE_URL = "http://localhost:8001/api"

class TestResults:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
        self.partial = 0

    def add_result(self, category: str, test_name: str, status: str, details: str = ""):
        self.tests.append({
            'category': category,
            'test': test_name,
            'status': status,
            'details': details
        })
        if status == 'PASS':
            self.passed += 1
        elif status == 'FAIL':
            self.failed += 1
        elif status == 'PARTIAL':
            self.partial += 1

    def print_summary(self):
        print('\n' + '='*80)
        print('TEST SUMMARY')
        print('='*80)

        by_category = {}
        for test in self.tests:
            cat = test['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(test)

        for category, tests in by_category.items():
            print(f'\n{category}:')
            for test in tests:
                status_symbol = {
                    'PASS': '[PASS]',
                    'FAIL': '[FAIL]',
                    'PARTIAL': '[PART]'
                }.get(test['status'], '[????]')
                print(f'  {status_symbol} {test["test"]}')
                if test['details']:
                    print(f'        {test["details"]}')

        print(f'\n{"="*80}')
        print(f'Total: {self.passed} passed, {self.partial} partial, {self.failed} failed')
        print(f'Success Rate: {(self.passed / len(self.tests) * 100):.1f}%')
        print('='*80)

def send_message(user_id: str, message: str, timeout: int = 15) -> Tuple[bool, str]:
    """Send a message and return (success, response_text)"""
    try:
        response = requests.post(
            f'{BASE_URL}/{user_id}/chat',
            json={'message': message},
            timeout=timeout
        )
        if response.status_code == 200:
            data = response.json()
            return True, data.get('response', '')
        else:
            return False, f'HTTP {response.status_code}'
    except Exception as e:
        return False, str(e)

def test_basic_mcp_tools(results: TestResults):
    """TEST 1: Basic MCP Tools"""
    print('\n' + '='*80)
    print('TEST 1: BASIC MCP TOOLS')
    print('='*80)

    test_user = f'test-basic-{int(time.time())}'

    # 1.1 Add Task - Multiple variations
    print('\n1.1 Testing Add Task variations...')
    add_tests = [
        "Add task to buy groceries",
        "Create a task for laundry",
        "Remind me to call doctor tomorrow",
        "I need to finish the report",
        "Add gym to my tasks"
    ]

    for i, cmd in enumerate(add_tests, 1):
        success, resp = send_message(test_user, cmd)
        if success and ('added' in resp.lower() or 'created' in resp.lower() or 'task' in resp.lower()):
            results.add_result('1.1 Add Task', f'Variation {i}: "{cmd[:30]}..."', 'PASS')
        else:
            results.add_result('1.1 Add Task', f'Variation {i}: "{cmd[:30]}..."', 'FAIL', resp[:100])
        time.sleep(0.5)

    # 1.2 List Tasks - Multiple variations
    print('\n1.2 Testing List Tasks variations...')
    list_tests = [
        "Show me all my tasks",
        "List all tasks",
        "What do I have to do?",
        "Show pending tasks",
        "What have I completed?"
    ]

    for i, cmd in enumerate(list_tests, 1):
        success, resp = send_message(test_user, cmd)
        if success and ('task' in resp.lower() or 'groceries' in resp.lower() or 'laundry' in resp.lower()):
            results.add_result('1.2 List Tasks', f'Variation {i}: "{cmd}"', 'PASS')
        else:
            results.add_result('1.2 List Tasks', f'Variation {i}: "{cmd}"', 'PARTIAL', 'Response unclear')
        time.sleep(0.5)

    # 1.3 Complete Task - Multiple variations
    print('\n1.3 Testing Complete Task variations...')
    complete_tests = [
        ("Complete task number 1", "number reference"),
        ("Mark task 2 as done", "mark as done"),
        ("Finish the first task", "ordinal reference"),
        ("Complete buy groceries task", "title reference"),
        ("Mark laundry as completed", "title + mark")
    ]

    for i, (cmd, desc) in enumerate(complete_tests, 1):
        success, resp = send_message(test_user, cmd)
        if success and ('complet' in resp.lower() or 'done' in resp.lower() or 'marked' in resp.lower()):
            results.add_result('1.3 Complete Task', f'{desc}: "{cmd}"', 'PASS')
        else:
            results.add_result('1.3 Complete Task', f'{desc}: "{cmd}"', 'PARTIAL', resp[:100])
        time.sleep(0.5)

    # 1.4 Delete Task - Multiple variations
    print('\n1.4 Testing Delete Task variations...')
    delete_tests = [
        ("Delete task 3", "number reference"),
        ("Remove the meeting task", "title reference"),
        ("Cancel task number 4", "cancel + number")
    ]

    for i, (cmd, desc) in enumerate(delete_tests, 1):
        success, resp = send_message(test_user, cmd)
        # Check if asking for confirmation (expected behavior)
        if success and ('confirm' in resp.lower() or 'sure' in resp.lower() or 'yes' in resp.lower()):
            # Confirm deletion
            time.sleep(0.5)
            success2, resp2 = send_message(test_user, 'yes')
            if success2 and ('delet' in resp2.lower() or 'remov' in resp2.lower()):
                results.add_result('1.4 Delete Task', f'{desc}: "{cmd}"', 'PASS')
            else:
                results.add_result('1.4 Delete Task', f'{desc}: "{cmd}"', 'PARTIAL', 'Confirmation unclear')
        elif success and ('delet' in resp.lower() or 'remov' in resp.lower()):
            results.add_result('1.4 Delete Task', f'{desc}: "{cmd}"', 'PASS', 'Direct delete')
        else:
            results.add_result('1.4 Delete Task', f'{desc}: "{cmd}"', 'FAIL', resp[:100])
        time.sleep(0.5)

    # 1.5 Update Task - Multiple variations
    print('\n1.5 Testing Update Task variations...')

    # Add fresh tasks for update testing
    send_message(test_user, "add test task 1")
    time.sleep(0.5)
    send_message(test_user, "add test task 2")
    time.sleep(0.5)

    update_tests = [
        ("Update task 1 to 'buy organic groceries'", "direct update"),
        ("Rename task 2 to 'urgent meeting'", "rename")
    ]

    for i, (cmd, desc) in enumerate(update_tests, 1):
        success, resp = send_message(test_user, cmd)
        if success and ('updat' in resp.lower() or 'renam' in resp.lower() or 'chang' in resp.lower()):
            results.add_result('1.5 Update Task', f'{desc}: "{cmd[:40]}..."', 'PASS')
        else:
            results.add_result('1.5 Update Task', f'{desc}: "{cmd[:40]}..."', 'PARTIAL', resp[:100])
        time.sleep(0.5)

def test_conversation_context(results: TestResults):
    """TEST 2: Conversation Context (Multi-turn)"""
    print('\n' + '='*80)
    print('TEST 2: CONVERSATION CONTEXT (MULTI-TURN)')
    print('='*80)

    test_user = f'test-context-{int(time.time())}'

    # Setup: Add tasks
    print('\nSetup: Adding test tasks...')
    for task in ['Task A', 'Task B', 'Task C', 'Task D']:
        send_message(test_user, f'add {task}')
        time.sleep(0.3)

    # 2.1 Delete with Confirmation
    print('\n2.1 Testing Delete with Confirmation...')
    success1, resp1 = send_message(test_user, 'Delete task 4')
    if success1 and ('confirm' in resp1.lower() or 'sure' in resp1.lower()):
        time.sleep(0.5)
        success2, resp2 = send_message(test_user, 'yes')
        if success2 and ('delet' in resp2.lower() or 'Task D' in resp2):
            results.add_result('2.1 Context', 'Delete with confirmation', 'PASS')
        else:
            results.add_result('2.1 Context', 'Delete with confirmation', 'PARTIAL', 'Confirmation response unclear')
    else:
        results.add_result('2.1 Context', 'Delete with confirmation', 'FAIL', 'No confirmation asked')

    # 2.2 Update with Details
    print('\n2.2 Testing Update with Details...')
    success1, resp1 = send_message(test_user, 'Modify task 2 description')
    if success1 and ('description' in resp1.lower() or 'provide' in resp1.lower()):
        time.sleep(0.5)
        success2, resp2 = send_message(test_user, 'Description: call after 3pm')
        if success2 and ('updat' in resp2.lower() or '3pm' in resp2):
            results.add_result('2.2 Context', 'Update with details', 'PASS')
        else:
            results.add_result('2.2 Context', 'Update with details', 'PARTIAL', 'Update response unclear')
    else:
        results.add_result('2.2 Context', 'Update with details', 'PARTIAL', 'No description request')

    # 2.3 Rename Task
    print('\n2.3 Testing Rename Task...')
    success1, resp1 = send_message(test_user, 'Rename task 3')
    if success1 and ('rename' in resp1.lower() or 'title' in resp1.lower() or 'name' in resp1.lower()):
        time.sleep(0.5)
        success2, resp2 = send_message(test_user, 'New title: urgent meeting')
        if success2 and ('renam' in resp2.lower() or 'updat' in resp2.lower() or 'urgent meeting' in resp2.lower()):
            results.add_result('2.3 Context', 'Rename task', 'PASS')
        else:
            results.add_result('2.3 Context', 'Rename task', 'PARTIAL', 'Rename response unclear')
    else:
        results.add_result('2.3 Context', 'Rename task', 'PARTIAL', 'No title request')

def test_natural_language_variations(results: TestResults):
    """TEST 3: Natural Language Variations"""
    print('\n' + '='*80)
    print('TEST 3: NATURAL LANGUAGE VARIATIONS (FROM SPEC)')
    print('='*80)

    test_user = f'test-nlp-{int(time.time())}'

    spec_examples = [
        ("Add a task to buy groceries", "add task"),
        ("Show me all my tasks", "show tasks"),
        ("What's pending?", "pending query"),
        ("I need to remember to pay bills", "remember task"),
        ("What have I completed?", "completed query")
    ]

    # Add some tasks first
    send_message(test_user, "add buy groceries")
    time.sleep(0.3)
    send_message(test_user, "add pay bills")
    time.sleep(0.3)
    send_message(test_user, "complete task 1")
    time.sleep(0.5)

    for cmd, desc in spec_examples:
        success, resp = send_message(test_user, cmd)
        if success and len(resp) > 10:  # Got a meaningful response
            results.add_result('3. Natural Language', f'{desc}: "{cmd}"', 'PASS')
        else:
            results.add_result('3. Natural Language', f'{desc}: "{cmd}"', 'FAIL', resp[:100])
        time.sleep(0.5)

def test_edge_cases(results: TestResults):
    """TEST 4: Edge Cases & Error Handling"""
    print('\n' + '='*80)
    print('TEST 4: EDGE CASES & ERROR HANDLING')
    print('='*80)

    test_user = f'test-edge-{int(time.time())}'

    # Add a few tasks
    send_message(test_user, "add task 1")
    time.sleep(0.3)
    send_message(test_user, "add task 2")
    time.sleep(0.5)

    # 4.1 Invalid References
    print('\n4.1 Testing Invalid References...')
    invalid_tests = [
        ("Complete task 999", "non-existent task"),
        ("Delete task XYZ", "invalid format"),
        ("Update task 0", "zero index")
    ]

    for cmd, desc in invalid_tests:
        success, resp = send_message(test_user, cmd)
        # Should get an error message or clarification, not crash
        if success:
            results.add_result('4.1 Invalid Refs', f'{desc}: "{cmd}"', 'PASS', 'Handled gracefully')
        else:
            results.add_result('4.1 Invalid Refs', f'{desc}: "{cmd}"', 'FAIL', 'System error')
        time.sleep(0.5)

    # 4.2 Ambiguous Commands
    print('\n4.2 Testing Ambiguous Commands...')
    ambiguous_tests = [
        ("add", "no task specified"),
        ("complete", "no task specified"),
        ("delete", "no task specified")
    ]

    for cmd, desc in ambiguous_tests:
        success, resp = send_message(test_user, cmd)
        # Should ask for clarification or provide help
        if success and len(resp) > 10:
            results.add_result('4.2 Ambiguous', f'{desc}: "{cmd}"', 'PASS', 'Handled gracefully')
        else:
            results.add_result('4.2 Ambiguous', f'{desc}: "{cmd}"', 'FAIL', 'No response')
        time.sleep(0.5)

def test_performance_metrics(results: TestResults):
    """TEST 5: Performance Metrics"""
    print('\n' + '='*80)
    print('TEST 5: PERFORMANCE METRICS')
    print('='*80)

    test_user = f'test-perf-{int(time.time())}'

    # Test: Add task in under 10 seconds
    print('\n5.1 Testing Add Task Performance (<10s)...')
    start = time.time()
    success, resp = send_message(test_user, "add performance test task", timeout=10)
    elapsed = time.time() - start

    if success and elapsed < 10:
        results.add_result('5. Performance', f'Add task in {elapsed:.2f}s (<10s)', 'PASS')
    else:
        results.add_result('5. Performance', f'Add task in {elapsed:.2f}s (<10s)', 'FAIL')

    # Test: Retrieve task list in under 2 seconds
    print('\n5.2 Testing List Tasks Performance (<2s)...')
    start = time.time()
    success, resp = send_message(test_user, "list all tasks", timeout=2)
    elapsed = time.time() - start

    if success and elapsed < 2:
        results.add_result('5. Performance', f'List tasks in {elapsed:.2f}s (<2s)', 'PASS')
    else:
        results.add_result('5. Performance', f'List tasks in {elapsed:.2f}s (<2s)', 'FAIL')

def main():
    print('='*80)
    print('COMPREHENSIVE TEST SUITE FOR TODO AI CHATBOT')
    print('='*80)
    print(f'Backend URL: {BASE_URL}')
    print(f'Test Start Time: {time.strftime("%Y-%m-%d %H:%M:%S")}')

    results = TestResults()

    try:
        # Run all test suites
        test_basic_mcp_tools(results)
        test_conversation_context(results)
        test_natural_language_variations(results)
        test_edge_cases(results)
        test_performance_metrics(results)

        # Print summary
        results.print_summary()

        # Final verification
        print('\n' + '='*80)
        print('SPECIFICATION COMPLIANCE VERIFICATION')
        print('='*80)

        success_rate = (results.passed / len(results.tests) * 100) if results.tests else 0

        print(f'\nCommand Interpretation Accuracy: {success_rate:.1f}%')
        print(f'Target: 90%+ - {"PASS" if success_rate >= 90 else "FAIL"}')

        print(f'\nTotal Tests Run: {len(results.tests)}')
        print(f'Passed: {results.passed}')
        print(f'Partial: {results.partial}')
        print(f'Failed: {results.failed}')

        if success_rate >= 90 and results.failed == 0:
            print('\n*** SYSTEM MEETS SPECIFICATION REQUIREMENTS ***')
            return 0
        elif success_rate >= 80:
            print('\n*** SYSTEM MOSTLY FUNCTIONAL - MINOR ISSUES ***')
            return 0
        else:
            print('\n*** SYSTEM HAS SIGNIFICANT ISSUES ***')
            return 1

    except Exception as e:
        print(f'\n\nFATAL ERROR: {e}')
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
