"""Authentication router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from runcoach.database import get_db
from runcoach.dependencies import get_current_user
from runcoach.models.user import User
from runcoach.schemas.auth import (
    MessageResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from runcoach.services.auth import (
    SESSION_MAX_AGE,
    authenticate_user,
    create_session_token,
    create_user,
    get_user_by_email,
    get_user_by_invite_code,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Register a new user with an invite code."""
    # Check if invite code is already used
    existing_invite = await get_user_by_invite_code(db, data.invite_code)
    if existing_invite is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite code already used",
        )

    # Check if email is already registered
    existing_email = await get_user_by_email(db, data.email)
    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = await create_user(
        db=db,
        invite_code=data.invite_code,
        name=data.name,
        email=data.email,
        password=data.password,
    )

    # Set session cookie
    session_token = create_session_token(user.id)
    response.set_cookie(
        key="session",
        value=session_token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return user


@router.post("/login", response_model=UserResponse)
async def login(
    data: UserLogin,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Login with email and password."""
    user = await authenticate_user(db, data.email, data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Set session cookie
    session_token = create_session_token(user.id)
    response.set_cookie(
        key="session",
        value=session_token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return user


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response) -> MessageResponse:
    """Logout and clear the session cookie."""
    response.delete_cookie(key="session")
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get the current authenticated user."""
    return current_user
