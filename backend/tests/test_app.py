"""Basic app tests."""

import pytest
from fastapi.testclient import TestClient

from runcoach.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_models_import():
    """Test that all models can be imported."""
    from runcoach.models import (
        User,
        StravaToken,
        UserProfile,
        Goal,
        TrainingPlan,
        Workout,
        WorkoutEdit,
        StravaActivity,
        WorkoutCompletion,
        ChatMessage,
        UserMemorySummary,
        Notification,
    )

    assert User.__tablename__ == "users"
    assert StravaToken.__tablename__ == "strava_tokens"
    assert UserProfile.__tablename__ == "user_profiles"
    assert Goal.__tablename__ == "goals"
    assert TrainingPlan.__tablename__ == "training_plans"
    assert Workout.__tablename__ == "workouts"
    assert WorkoutEdit.__tablename__ == "workout_edits"
    assert StravaActivity.__tablename__ == "strava_activities"
    assert WorkoutCompletion.__tablename__ == "workout_completions"
    assert ChatMessage.__tablename__ == "chat_messages"
    assert UserMemorySummary.__tablename__ == "user_memory_summaries"
    assert Notification.__tablename__ == "notifications"
