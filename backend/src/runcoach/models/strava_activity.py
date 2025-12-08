"""Strava activity model."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from runcoach.database import Base


class StravaActivity(Base):
    """Raw Strava activity data."""

    __tablename__ = "strava_activities"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    strava_activity_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
    )
    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    activity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(nullable=True)
    distance_meters: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    moving_time_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    elapsed_time_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    average_heartrate: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    max_heartrate: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    average_pace_seconds_per_meter: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 6),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    __table_args__ = (
        Index("idx_strava_activities_user_date", "user_id", "start_date"),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="strava_activities")
    workout_completions: Mapped[list["WorkoutCompletion"]] = relationship(
        "WorkoutCompletion",
        back_populates="strava_activity",
    )
