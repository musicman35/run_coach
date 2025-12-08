"""initial_schema

Revision ID: 4f7102b89d74
Revises:
Create Date: 2025-12-08 12:45:27.389569

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4f7102b89d74'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables."""
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('invite_code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invite_code'),
        sa.UniqueConstraint('email'),
    )

    # Strava tokens
    op.create_table(
        'strava_tokens',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('strava_athlete_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # User profiles
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('current_weekly_mileage_miles', sa.Numeric(5, 2), nullable=True),
        sa.Column('days_available_per_week', sa.Integer(), nullable=True),
        sa.Column('easy_pace_per_mile_seconds', sa.Integer(), nullable=True),
        sa.Column('injury_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id'),
    )

    # Goals
    op.create_table(
        'goals',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('goal_type', sa.String(20), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_race_distance_meters', sa.Integer(), nullable=True),
        sa.Column('target_race_date', sa.Date(), nullable=True),
        sa.Column('target_time_seconds', sa.Integer(), nullable=True),
        sa.Column('target_weekly_mileage_miles', sa.Numeric(5, 2), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('flagged_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_goals_user_status', 'goals', ['user_id', 'status'])

    # Training plans
    op.create_table(
        'training_plans',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('goal_id', sa.UUID(), nullable=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('methodology', sa.String(100), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('generation_context', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='SET NULL'),
    )

    # Workouts
    op.create_table(
        'workouts',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('training_plan_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('workout_type', sa.String(30), nullable=False),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('structure', postgresql.JSONB(), nullable=False),
        sa.Column('estimated_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('estimated_distance_meters', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='scheduled'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['training_plan_id'], ['training_plans.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_workouts_user_date', 'workouts', ['user_id', 'scheduled_date'])

    # Workout edits
    op.create_table(
        'workout_edits',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('workout_id', sa.UUID(), nullable=False),
        sa.Column('edited_by', sa.String(20), nullable=False),
        sa.Column('previous_structure', postgresql.JSONB(), nullable=False),
        sa.Column('new_structure', postgresql.JSONB(), nullable=False),
        sa.Column('edit_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['workout_id'], ['workouts.id'], ondelete='CASCADE'),
    )

    # Strava activities
    op.create_table(
        'strava_activities',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('strava_activity_id', sa.BigInteger(), nullable=False),
        sa.Column('raw_data', postgresql.JSONB(), nullable=False),
        sa.Column('activity_type', sa.String(50), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('distance_meters', sa.Numeric(10, 2), nullable=True),
        sa.Column('moving_time_seconds', sa.Integer(), nullable=True),
        sa.Column('elapsed_time_seconds', sa.Integer(), nullable=True),
        sa.Column('average_heartrate', sa.Numeric(5, 2), nullable=True),
        sa.Column('max_heartrate', sa.Numeric(5, 2), nullable=True),
        sa.Column('average_pace_seconds_per_meter', sa.Numeric(10, 6), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('strava_activity_id'),
    )
    op.create_index('idx_strava_activities_user_date', 'strava_activities', ['user_id', 'start_date'])

    # Workout completions
    op.create_table(
        'workout_completions',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('workout_id', sa.UUID(), nullable=False),
        sa.Column('strava_activity_id', sa.UUID(), nullable=True),
        sa.Column('completion_status', sa.String(20), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['workout_id'], ['workouts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['strava_activity_id'], ['strava_activities.id'], ondelete='SET NULL'),
    )

    # Chat messages
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('context_snapshot', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_chat_messages_user', 'chat_messages', ['user_id', 'created_at'])

    # User memory summaries
    op.create_table(
        'user_memory_summaries',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('summary_type', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source_date_range_start', sa.Date(), nullable=True),
        sa.Column('source_date_range_end', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Notifications
    op.create_table(
        'notifications',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('notification_type', sa.String(30), nullable=False),
        sa.Column('channel', sa.String(20), nullable=False),
        sa.Column('subject', sa.String(200), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('scheduled_for', sa.DateTime(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_notifications_scheduled', 'notifications', ['status', 'scheduled_for'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index('idx_notifications_scheduled', 'notifications')
    op.drop_table('notifications')
    op.drop_table('user_memory_summaries')
    op.drop_index('idx_chat_messages_user', 'chat_messages')
    op.drop_table('chat_messages')
    op.drop_table('workout_completions')
    op.drop_index('idx_strava_activities_user_date', 'strava_activities')
    op.drop_table('strava_activities')
    op.drop_table('workout_edits')
    op.drop_index('idx_workouts_user_date', 'workouts')
    op.drop_table('workouts')
    op.drop_table('training_plans')
    op.drop_index('idx_goals_user_status', 'goals')
    op.drop_table('goals')
    op.drop_table('user_profiles')
    op.drop_table('strava_tokens')
    op.drop_table('users')
