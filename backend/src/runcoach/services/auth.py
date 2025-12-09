"""Authentication service for password hashing and session management."""

import uuid

import bcrypt
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from runcoach.config import get_settings
from runcoach.models.user import User

settings = get_settings()

# Session serializer
session_serializer = URLSafeTimedSerializer(settings.secret_key)

# Session duration (7 days)
SESSION_MAX_AGE = 60 * 60 * 24 * 7


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_session_token(user_id: uuid.UUID) -> str:
    """Create a signed session token containing the user ID."""
    return session_serializer.dumps(str(user_id))


def verify_session_token(token: str) -> uuid.UUID | None:
    """Verify a session token and return the user ID if valid."""
    try:
        user_id_str = session_serializer.loads(token, max_age=SESSION_MAX_AGE)
        return uuid.UUID(user_id_str)
    except (BadSignature, SignatureExpired, ValueError):
        return None


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get a user by email address."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Get a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_invite_code(db: AsyncSession, invite_code: str) -> User | None:
    """Get a user by invite code."""
    result = await db.execute(select(User).where(User.invite_code == invite_code))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    invite_code: str,
    name: str,
    email: str,
    password: str,
) -> User:
    """Create a new user."""
    user = User(
        invite_code=invite_code,
        name=name,
        email=email,
        password_hash=hash_password(password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    """Authenticate a user by email and password."""
    user = await get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
