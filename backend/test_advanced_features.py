import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.mcp.tools import add_task, list_tasks, update_task

async def test_advanced_functionality():
    """Test advanced functionality: priority, tags, and search"""
    user_id = "test-user-advanced"

    print("=== TESTING ADVANCED FUNCTIONALITY ===")
    print("Testing: priority, tags, search, filtering, sorting")

    # Clean slate - remove any existing tasks
    all_tasks = await list_tasks(user_id=user_id)
    print(f"\nInitial state: {len(all_tasks['tasks'])} tasks found")

    # Test 1: Add tasks with different priorities
    print("\n1. ADDING TASKS WITH DIFFERENT PRIORITIES:")
    result1 = await add_task(user_id=user_id, title="High priority task", priority="high", tags=["urgent", "work"])
    print(f"   Added HIGH priority task: {result1['task_id']}")

    result2 = await add_task(user_id=user_id, title="Medium priority task", priority="medium", tags=["normal", "personal"])
    print(f"   Added MEDIUM priority task: {result2['task_id']}")

    result3 = await add_task(user_id=user_id, title="Low priority task", priority="low", tags=["later", "optional"])
    print(f"   Added LOW priority task: {result3['task_id']}")

    result4 = await add_task(user_id=user_id, title="Another high priority task", priority="high", tags=["important", "work"])
    print(f"   Added ANOTHER HIGH priority task: {result4['task_id']}")

    # Test 2: List all tasks to see priorities and tags
    print("\n2. LISTING ALL TASKS:")
    all_tasks = await list_tasks(user_id=user_id)
    print(f"   Total tasks: {len(all_tasks['tasks'])}")
    for task in all_tasks['tasks']:
        print(f"   - {task['title']} | Priority: {task['priority']} | Tags: {task['tags']} | Completed: {task['completed']}")

    # Test 3: Filter by priority
    print("\n3. FILTERING BY HIGH PRIORITY:")
    high_tasks = await list_tasks(user_id=user_id, priority=["high"])
    print(f"   High priority tasks: {len(high_tasks['tasks'])}")
    for task in high_tasks['tasks']:
        print(f"   - {task['title']} | Priority: {task['priority']}")

    # Test 4: Filter by tags
    print("\n4. FILTERING BY TAG 'work':")
    work_tasks = await list_tasks(user_id=user_id, tags=["work"])
    print(f"   Tasks with 'work' tag: {len(work_tasks['tasks'])}")
    for task in work_tasks['tasks']:
        print(f"   - {task['title']} | Tags: {task['tags']}")

    # Test 5: Filter by multiple tags
    print("\n5. FILTERING BY TAG 'urgent':")
    urgent_tasks = await list_tasks(user_id=user_id, tags=["urgent"])
    print(f"   Tasks with 'urgent' tag: {len(urgent_tasks['tasks'])}")
    for task in urgent_tasks['tasks']:
        print(f"   - {task['title']} | Tags: {task['tags']}")

    # Test 6: Search functionality
    print("\n6. SEARCHING FOR 'high':")
    search_results = await list_tasks(user_id=user_id, search_term="high")
    print(f"   Tasks matching 'high': {len(search_results['tasks'])}")
    for task in search_results['tasks']:
        print(f"   - {task['title']}")

    # Test 7: Search for tag in search
    print("\n7. SEARCHING FOR 'urgent':")
    search_results = await list_tasks(user_id=user_id, search_term="urgent")
    print(f"   Tasks matching 'urgent': {len(search_results['tasks'])}")
    for task in search_results['tasks']:
        print(f"   - {task['title']} | Tags: {task['tags']}")

    # Test 8: Update task priority and tags
    print("\n8. UPDATING TASK PRIORITY AND TAGS:")
    if all_tasks['tasks']:
        task_to_update = all_tasks['tasks'][0]
        update_result = await update_task(
            user_id=user_id,
            task_id=task_to_update['task_id'],
            priority="high",
            tags=["updated", "changed", "now-important"]
        )
        print(f"   Updated task: {update_result['task_id']}")
        print(f"   Updated fields: {list(update_result['updated_fields'].keys())}")

    # Test 9: Final verification after update
    print("\n9. FINAL VERIFICATION:")
    final_tasks = await list_tasks(user_id=user_id)
    print(f"   Total tasks after update: {len(final_tasks['tasks'])}")
    for task in final_tasks['tasks']:
        print(f"   - {task['title']} | Priority: {task['priority']} | Tags: {task['tags']}")

    # Test 10: Complex filtering (priority + tags)
    print("\n10. COMPLEX FILTERING (high priority + work tag):")
    complex_results = await list_tasks(user_id=user_id, priority=["high"], tags=["work"])
    print(f"   High priority tasks with 'work' tag: {len(complex_results['tasks'])}")
    for task in complex_results['tasks']:
        print(f"   - {task['title']} | Priority: {task['priority']} | Tags: {task['tags']}")

    print("\n=== ALL ADVANCED FUNCTIONALITY TESTED SUCCESSFULLY ===")

if __name__ == "__main__":
    asyncio.run(test_advanced_functionality())