import asyncio
from tools import add_task, complete_task, list_tasks


async def test_complete_task():
    """
    Test the complete_task function
    """
    try:
        # First, add a task to test with
        task_result = await add_task(
            user_id="test_user_123",
            title="Test task to complete",
            description="This is a test task"
        )
        print(f"Created task: {task_result}")

        # Test completing the task
        complete_result = await complete_task(
            user_id="test_user_123",
            task_id=task_result["task_id"]
        )
        print(f"Completed task: {complete_result}")

        # Verify the task is now completed by listing tasks
        tasks_result = await list_tasks(
            user_id="test_user_123",
            completed=None  # List all tasks
        )
        print(f"Tasks after completion: {len(tasks_result['tasks'])}")
        for task in tasks_result["tasks"]:
            if task["task_id"] == task_result["task_id"]:
                print(f"Verified task status: completed={task['completed']}")

        # Test idempotency - try to complete the same task again
        idempotent_result = await complete_task(
            user_id="test_user_123",
            task_id=task_result["task_id"]
        )
        print(f"Idempotent completion result: {idempotent_result}")

    except Exception as e:
        print(f"Error testing complete_task: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_complete_task())