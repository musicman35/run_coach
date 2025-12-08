"""Workout edit history model."""

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from runcoach.database import Base


class WorkoutEdit(Base):
    """History of edits made to a workout."""

    __tablename__ = "workout_edits"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    workout_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workouts.id", ondelete="CASCADE"),
        nullable=False,
    )
    edited_by: Mapped[str] = mapped_column(String(20), nullable=False)
    previous_structure: Mapped[dict] = mapped_column(JSONB, nullable=False)
    new_structure: Mapped[dict] = mapped_column(JSONB, nullable=False)
    edit_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    workout: Mapped["Workout"] = relationship("Workout", back_populates="edits")
