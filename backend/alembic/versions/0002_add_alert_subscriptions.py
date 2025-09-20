"""add_alert_subscriptions_table"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0002_add_alert_subscriptions'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'alert_subscriptions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('subscriber_id', sa.String(length=128), nullable=False),
        sa.Column('label', sa.String(length=128), nullable=False),
        sa.Column('categories', sa.JSON(), nullable=False, server_default=sa.text('[]')),
        sa.Column('entities', sa.JSON(), nullable=False, server_default=sa.text('[]')),
        sa.Column('severities', sa.JSON(), nullable=False, server_default=sa.text('[]')),
        sa.Column('min_severity', sa.String(length=32), nullable=True),
        sa.Column('channels', sa.JSON(), nullable=False, server_default=sa.text('[]')),
        sa.Column('delivery_window_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivery_window_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('mute_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('last_notified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_alert_subscriptions_subscriber_id', 'alert_subscriptions', ['subscriber_id'])
    op.create_index('ix_alert_subscriptions_is_active', 'alert_subscriptions', ['is_active'])


def downgrade() -> None:
    op.drop_index('ix_alert_subscriptions_is_active', table_name='alert_subscriptions')
    op.drop_index('ix_alert_subscriptions_subscriber_id', table_name='alert_subscriptions')
    op.drop_table('alert_subscriptions')
