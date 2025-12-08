"""Workout completion model."""

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from runcoach.database import Base


class WorkoutCompletion(Base):
    """Links completed Strava activities to scheduled workouts."""

    __tablename__ = "workout_completions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    workout_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workouts.id", ondelete="CASCADE"),
        nullable=False,
    )
    strava_activity_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("strava_activities.id", ondelete="SET NULL"),
        nullable=True,
    )
    completion_status: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    workout: Mapped["Workout"] = relationship("Workout", back_populates="completions")
    strava_activity: Mapped["StravaActivity | None"] = relationship(
        "StravaActivity",
        back_populates="workout_completions",
    )
