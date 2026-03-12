import asyncio
from src.services.database import async_engine
from sqlalchemy import text

async def test_db_connection():
    try:
        async with async_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("Database connection successful")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_db_connection())
    print(f"Connection test result: {'Success' if success else 'Failed'}")