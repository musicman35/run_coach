"""FastAPI dependencies."""

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from runcoach.database import get_db
from runcoach.models.user import User
from runcoach.services.auth import get_user_by_id, verify_session_token


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
) -> User:
    """Get the current authenticated user from the session cookie."""
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    user_id = verify_session_token(session)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_current_user_optional(
    db: Annotated[AsyncSession, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
) -> User | None:
    """Get the current user if authenticated, otherwise None."""
    if session is None:
        return None

    user_id = verify_session_token(session)
    if user_id is None:
        return None

    return await get_user_by_id(db, user_id)
