from src.mcp.tools import list_tasks
import asyncio

async def test_tool():
    try:
        print("Testing list_tasks tool directly...")
        result = await list_tasks(user_id='test_user_123', priority=['high'])
        print('Direct tool test result:', result)
    except Exception as e:
        print('Error in direct tool test:', str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tool())