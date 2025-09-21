"""add_legislative_bill_versions_table"""

from alembic import op
import sqlalchemy as sa

revision = '0004_add_legislative_bill_versions'
down_revision = '0003_add_authentication'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'legislative_bill_versions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('bill_id', sa.String(length=64), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_legislative_bill_versions_bill_id', 'legislative_bill_versions', ['bill_id'])
    op.create_unique_constraint('uq_bill_version', 'legislative_bill_versions', ['bill_id', 'version'])


def downgrade() -> None:
    op.drop_constraint('uq_bill_version', 'legislative_bill_versions', type_='unique')
    op.drop_index('ix_legislative_bill_versions_bill_id', table_name='legislative_bill_versions')
    op.drop_table('legislative_bill_versions')
