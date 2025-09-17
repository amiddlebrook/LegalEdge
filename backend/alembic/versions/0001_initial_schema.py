"""initial schema"""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'legislative_bills',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('bill_id', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('stage', sa.String(length=128), nullable=False),
        sa.Column('jurisdiction', sa.String(length=128), nullable=False),
        sa.Column('committees', sa.JSON(), nullable=False, server_default=sa.text('[]')),
        sa.Column('sectors', sa.JSON(), nullable=False, server_default=sa.text('[]')),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('next_action_date', sa.Date(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('probability_of_enactment', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('bill_id'),
    )
    op.create_index('ix_legislative_bills_bill_id', 'legislative_bills', ['bill_id'], unique=True)
    op.create_index('ix_legislative_bills_jurisdiction', 'legislative_bills', ['jurisdiction'])
    op.create_index('ix_legislative_bills_last_updated', 'legislative_bills', ['last_updated'])

    op.create_table(
        'forecast_signals',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('sector', sa.String(length=128), nullable=False),
        sa.Column('ticker', sa.String(length=16), nullable=False),
        sa.Column('thesis', sa.Text(), nullable=False),
        sa.Column('expected_return_pct', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('catalysts', sa.JSON(), nullable=False, server_default=sa.text('[]')),
        sa.Column('horizon_days', sa.Integer(), nullable=False, server_default=sa.text('30')),
        sa.Column('generated_on', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_forecast_signals_sector', 'forecast_signals', ['sector'])
    op.create_index('ix_forecast_signals_ticker', 'forecast_signals', ['ticker'])
    op.create_index('ix_forecast_signals_generated_on', 'forecast_signals', ['generated_on'])

    op.create_table(
        'policy_alerts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('alert_key', sa.String(length=128), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=32), nullable=False),
        sa.Column('raised_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('related_entities', sa.JSON(), nullable=False, server_default=sa.text('[]')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('alert_key'),
    )
    op.create_index('ix_policy_alerts_alert_key', 'policy_alerts', ['alert_key'], unique=True)
    op.create_index('ix_policy_alerts_category', 'policy_alerts', ['category'])
    op.create_index('ix_policy_alerts_raised_at', 'policy_alerts', ['raised_at'])

    op.create_table(
        'opportunity_recommendations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('ticker', sa.String(length=16), nullable=False),
        sa.Column('thesis', sa.Text(), nullable=False),
        sa.Column('expected_return_pct', sa.Float(), nullable=False),
        sa.Column('conviction', sa.Float(), nullable=False),
        sa.Column('horizon_days', sa.Integer(), nullable=False),
        sa.Column('catalysts', sa.JSON(), nullable=False, server_default=sa.text('[]')),
        sa.Column('risk_rating', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_opportunity_recommendations_ticker', 'opportunity_recommendations', ['ticker'])

    op.create_table(
        'trade_disclosures',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('member', sa.String(length=256), nullable=False),
        sa.Column('chamber', sa.String(length=32), nullable=False),
        sa.Column('ticker', sa.String(length=16), nullable=False),
        sa.Column('transaction_type', sa.String(length=32), nullable=False),
        sa.Column('transaction_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('amount_range', sa.String(length=64), nullable=False),
        sa.Column('related_bill', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_trade_disclosures_member', 'trade_disclosures', ['member'])
    op.create_index('ix_trade_disclosures_chamber', 'trade_disclosures', ['chamber'])
    op.create_index('ix_trade_disclosures_ticker', 'trade_disclosures', ['ticker'])
    op.create_index('ix_trade_disclosures_transaction_date', 'trade_disclosures', ['transaction_date'])


def downgrade() -> None:
    op.drop_index('ix_trade_disclosures_transaction_date', table_name='trade_disclosures')
    op.drop_index('ix_trade_disclosures_ticker', table_name='trade_disclosures')
    op.drop_index('ix_trade_disclosures_chamber', table_name='trade_disclosures')
    op.drop_index('ix_trade_disclosures_member', table_name='trade_disclosures')
    op.drop_table('trade_disclosures')
    op.drop_index('ix_opportunity_recommendations_ticker', table_name='opportunity_recommendations')
    op.drop_table('opportunity_recommendations')
    op.drop_index('ix_policy_alerts_raised_at', table_name='policy_alerts')
    op.drop_index('ix_policy_alerts_category', table_name='policy_alerts')
    op.drop_index('ix_policy_alerts_alert_key', table_name='policy_alerts')
    op.drop_table('policy_alerts')
    op.drop_index('ix_forecast_signals_generated_on', table_name='forecast_signals')
    op.drop_index('ix_forecast_signals_ticker', table_name='forecast_signals')
    op.drop_index('ix_forecast_signals_sector', table_name='forecast_signals')
    op.drop_table('forecast_signals')
    op.drop_index('ix_legislative_bills_last_updated', table_name='legislative_bills')
    op.drop_index('ix_legislative_bills_jurisdiction', table_name='legislative_bills')
    op.drop_index('ix_legislative_bills_bill_id', table_name='legislative_bills')
    op.drop_table('legislative_bills')
