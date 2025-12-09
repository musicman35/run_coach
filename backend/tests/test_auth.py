"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient

from runcoach.main import app
from runcoach.services.auth import (
    create_session_token,
    hash_password,
    verify_password,
    verify_session_token,
)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password("wrongpassword", hashed) is False


class TestSessionTokens:
    """Tests for session token functions."""

    def test_create_session_token(self):
        """Test creating session token."""
        import uuid

        user_id = uuid.uuid4()
        token = create_session_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_session_token_valid(self):
        """Test verifying valid session token."""
        import uuid

        user_id = uuid.uuid4()
        token = create_session_token(user_id)
        verified_id = verify_session_token(token)

        assert verified_id == user_id

    def test_verify_session_token_invalid(self):
        """Test verifying invalid session token."""
        verified_id = verify_session_token("invalid-token")

        assert verified_id is None

    def test_verify_session_token_tampered(self):
        """Test verifying tampered session token."""
        import uuid

        user_id = uuid.uuid4()
        token = create_session_token(user_id)
        tampered_token = token[:-5] + "xxxxx"
        verified_id = verify_session_token(tampered_token)

        assert verified_id is None


class TestAuthEndpoints:
    """Tests for auth endpoints (without database)."""

    def test_logout(self, client):
        """Test logout endpoint."""
        response = client.post("/auth/logout")

        assert response.status_code == 200
        assert response.json() == {"message": "Logged out successfully"}

    def test_get_me_unauthenticated(self, client):
        """Test /me endpoint without authentication."""
        response = client.get("/auth/me")

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_get_me_invalid_session(self, client):
        """Test /me endpoint with invalid session."""
        client.cookies.set("session", "invalid-token")
        response = client.get("/auth/me")

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired session"


class TestAuthSchemas:
    """Tests for auth schemas validation."""

    def test_user_register_schema_valid(self):
        """Test valid UserRegister schema."""
        from runcoach.schemas.auth import UserRegister

        data = UserRegister(
            invite_code="ABC123",
            name="Test User",
            email="test@example.com",
            password="securepassword123",
        )

        assert data.invite_code == "ABC123"
        assert data.name == "Test User"
        assert data.email == "test@example.com"
        assert data.password == "securepassword123"

    def test_user_register_schema_invalid_email(self):
        """Test UserRegister with invalid email."""
        from pydantic import ValidationError

        from runcoach.schemas.auth import UserRegister

        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                invite_code="ABC123",
                name="Test User",
                email="not-an-email",
                password="securepassword123",
            )

        assert "email" in str(exc_info.value)

    def test_user_register_schema_password_too_short(self):
        """Test UserRegister with password too short."""
        from pydantic import ValidationError

        from runcoach.schemas.auth import UserRegister

        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                invite_code="ABC123",
                name="Test User",
                email="test@example.com",
                password="short",
            )

        assert "password" in str(exc_info.value)

    def test_user_login_schema_valid(self):
        """Test valid UserLogin schema."""
        from runcoach.schemas.auth import UserLogin

        data = UserLogin(
            email="test@example.com",
            password="securepassword123",
        )

        assert data.email == "test@example.com"
        assert data.password == "securepassword123"
