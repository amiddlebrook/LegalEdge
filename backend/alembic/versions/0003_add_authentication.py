"""add_authentication_tables"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0003_add_authentication'
down_revision = '0002_add_alert_subscriptions'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('username', sa.String(length=128), nullable=False),
        sa.Column('hashed_password', sa.String(length=256), nullable=False),
        sa.Column('full_name', sa.String(length=256), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('provider', sa.String(length=64), nullable=True),
        sa.Column('provider_id', sa.String(length=256), nullable=True),
        sa.Column('avatar_url', sa.String(length=512), nullable=True),
        sa.Column('preferences', sa.JSON(), nullable=False, server_default=sa.text('{}')),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_is_active', 'users', ['is_active'])

    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('description', sa.String(length=256), nullable=False),
        sa.Column('permissions', sa.JSON(), nullable=False, server_default=sa.text('{}')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('name'),
    )
    op.create_index('ix_roles_name', 'roles', ['name'], unique=True)

    op.create_table(
        'user_roles',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_user_roles_user_id', 'user_roles', ['user_id'])
    op.create_index('ix_user_roles_role_id', 'user_roles', ['role_id'])

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=128), nullable=False),
        sa.Column('resource', sa.String(length=256), nullable=False),
        sa.Column('resource_id', sa.String(length=128), nullable=True),
        sa.Column('details', sa.JSON(), nullable=False, server_default=sa.text('{}')),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=512), nullable=True),
        sa.Column('method', sa.String(length=16), nullable=True),
        sa.Column('path', sa.String(length=2048), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_resource', 'audit_logs', ['resource'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_resource', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index('ix_user_roles_role_id', table_name='user_roles')
    op.drop_index('ix_user_roles_user_id', table_name='user_roles')
    op.drop_table('user_roles')
    op.drop_index('ix_roles_name', table_name='roles')
    op.drop_table('roles')
    op.drop_index('ix_users_is_active', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
