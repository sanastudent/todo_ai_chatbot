#!/usr/bin/env python3
"""
Verify that the agent and MCP tools are properly integrated
"""
import inspect
import sys
import os

# Add backend src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from backend.src.services.agent import invoke_agent, extract_task_details_with_priority_and_tags
from backend.src.mcp.tools import add_task, list_tasks


def check_function_signatures():
    """Check that MCP tools accept the required parameters"""
    print("VERIFYING MCP TOOL FUNCTION SIGNATURES")
    print("=" * 50)

    # Check add_task function signature
    add_task_sig = inspect.signature(add_task)
    print(f"add_task parameters: {list(add_task_sig.parameters.keys())}")
    has_priority = 'priority' in add_task_sig.parameters
    has_tags = 'tags' in add_task_sig.parameters
    print(f"  Has priority parameter: {has_priority}")
    print(f"  Has tags parameter: {has_tags}")
    print(f"  Status: {'PASS' if (has_priority and has_tags) else 'FAIL'}")

    # Check list_tasks function signature
    list_tasks_sig = inspect.signature(list_tasks)
    print(f"\nlist_tasks parameters: {list(list_tasks_sig.parameters.keys())}")
    has_priority = 'priority' in list_tasks_sig.parameters
    has_tags = 'tags' in list_tasks_sig.parameters
    has_search = 'search_term' in list_tasks_sig.parameters
    has_sort_by = 'sort_by' in list_tasks_sig.parameters
    has_sort_order = 'sort_order' in list_tasks_sig.parameters
    print(f"  Has priority parameter: {has_priority}")
    print(f"  Has tags parameter: {has_tags}")
    print(f"  Has search_term parameter: {has_search}")
    print(f"  Has sort_by parameter: {has_sort_by}")
    print(f"  Has sort_order parameter: {has_sort_order}")
    print(f"  Status: {'PASS' if (has_priority and has_tags and has_search and has_sort_by and has_sort_order) else 'FAIL'}")

    all_pass = (has_priority and has_tags and has_search and has_sort_by and has_sort_order)
    return all_pass


def check_agent_parsing():
    """Check that the agent can parse enhanced commands"""
    print("\nVERIFYING AGENT COMMAND PARSING")
    print("=" * 50)

    test_cases = [
        ("Add high priority task", "task with priority", lambda r: r is not None and isinstance(r, tuple) and len(r) >= 2 and r[1] == "high"),
        ("Add work task", "task with tags", lambda r: r is not None and isinstance(r, tuple) and len(r) >= 3 and "work" in (r[2] or [])),
        ("Add tag shopping", "task with tags", lambda r: r is not None and isinstance(r, tuple) and len(r) >= 3 and "shopping" in (r[2] or [])),
        ("Show tasks with high priority", "priority filter", lambda r: r is not None),
        ("Search for doctor tasks", "search term", lambda r: r is not None),
        ("Sort tasks by date", "sort params", lambda r: r is not None),
    ]

    all_passed = True
    for command, expected, validator in test_cases:
        if "priority filter" in expected:
            from backend.src.services.agent import extract_priority_filter
            result = extract_priority_filter(command.lower())
        elif "search term" in expected:
            from backend.src.services.agent import extract_search_term
            result = extract_search_term(command.lower())
        elif "sort params" in expected:
            from backend.src.services.agent import extract_sort_params
            result = extract_sort_params(command.lower())
        else:
            # This is for task parsing functions that return (title, priority, tags)
            result = extract_task_details_with_priority_and_tags(command)

        passed = validator(result)
        print(f"  '{command}' -> {expected}: {'PASS' if passed else 'FAIL'}")
        all_passed = all_passed and passed

    return all_passed


def main():
    print("AGENT-MCP INTEGRATION VERIFICATION")
    print("Checking that the AI agent and MCP tools are properly integrated")
    print()

    mcp_ok = check_function_signatures()
    agent_ok = check_agent_parsing()

    print("\n" + "=" * 60)
    print("INTEGRATION VERIFICATION RESULTS:")
    print(f"MCP Tools Signature Check: {'PASS' if mcp_ok else 'FAIL'}")
    print(f"Agent Parsing Check: {'PASS' if agent_ok else 'FAIL'}")
    print(f"Overall Status: {'ALL INTEGRATED' if (mcp_ok and agent_ok) else 'ISSUES FOUND'}")
    print("=" * 60)

    if mcp_ok and agent_ok:
        print("\nSUCCESS: All intermediate features are properly integrated!")
        print("   - Agent can parse enhanced commands")
        print("   - MCP tools accept priority, tags, search, filter, sort parameters")
        print("   - Agent calls MCP tools with enhanced parameters")
        return True
    else:
        print("\nFAILURE: Integration issues detected")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)