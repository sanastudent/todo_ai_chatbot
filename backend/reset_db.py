import asyncio
from sqlalchemy import text
from src.services.database import async_engine

async def reset_database():
    async with async_engine.begin() as conn:
        # Drop all tables
        await conn.execute(text('DROP TABLE IF EXISTS task'))
        await conn.execute(text('DROP TABLE IF EXISTS message'))
        await conn.execute(text('DROP TABLE IF EXISTS conversation'))
        print('Tables dropped')

    # Dispose of the engine
    await async_engine.dispose()
    print('Database reset complete')

if __name__ == "__main__":
    asyncio.run(reset_database())