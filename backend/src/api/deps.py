from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.services.database import async_engine


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Database dependency that provides an async database session
    """
    async with AsyncSession(async_engine) as session:
        yield session


def get_current_user(dummy_param: str = "unused") -> str:
    """
    Stub authentication dependency that returns the authenticated user_id
    In a real implementation, this would validate a JWT token
    For now, we'll bypass this and use the path parameter directly in the route
    """
    # TODO: Replace with real JWT validation using Better Auth
    # For now, this is a placeholder that will be bypassed
    return "placeholder_user"