import asyncio
from tools import list_tasks, add_task


async def test_list_tasks():
    """
    Test the list_tasks function
    """
    try:
        # First, add a few tasks to test with
        await add_task(
            user_id="test_user_123",
            title="First task",
            description="This is the first task"
        )

        await add_task(
            user_id="test_user_123",
            title="Second task"
        )

        # Test listing all tasks
        result = await list_tasks(user_id="test_user_123")
        print("All tasks for user:")
        for task in result["tasks"]:
            print(f"- {task['title']} (ID: {task['task_id']}, Completed: {task['completed']})")

        # Test with an empty user (should return empty list)
        result_empty = await list_tasks(user_id="nonexistent_user")
        print(f"\nTasks for nonexistent user: {len(result_empty['tasks'])}")

    except Exception as e:
        print(f"Error testing list_tasks: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_list_tasks())