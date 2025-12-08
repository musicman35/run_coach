"""Workout model."""

import uuid
from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from runcoach.database import Base


class Workout(Base):
    """Scheduled workout."""

    __tablename__ = "workouts"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    training_plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("training_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    workout_type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    structure: Mapped[dict] = mapped_column(JSONB, nullable=False)
    estimated_duration_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    estimated_distance_meters: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        Index("idx_workouts_user_date", "user_id", "scheduled_date"),
    )

    # Relationships
    training_plan: Mapped["TrainingPlan"] = relationship(
        "TrainingPlan",
        back_populates="workouts",
    )
    user: Mapped["User"] = relationship("User", back_populates="workouts")
    edits: Mapped[list["WorkoutEdit"]] = relationship(
        "WorkoutEdit",
        back_populates="workout",
        cascade="all, delete-orphan",
    )
    completions: Mapped[list["WorkoutCompletion"]] = relationship(
        "WorkoutCompletion",
        back_populates="workout",
        cascade="all, delete-orphan",
    )
