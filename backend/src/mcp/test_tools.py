import asyncio
from tools import add_task


async def test_add_task():
    """
    Test the add_task function directly
    """
    try:
        result = await add_task(
            user_id="test_user_123",
            title="Buy groceries",
            description="Milk, eggs, and bread"
        )
        print("Task created successfully:", result)
        print("Task ID:", result["task_id"])
        print("Title:", result["title"])
        print("Created at:", result["created_at"])
    except Exception as e:
        print(f"Error creating task: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_add_task())