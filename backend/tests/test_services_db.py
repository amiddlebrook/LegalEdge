import pytest
import pytest_asyncio
from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.ingestion.sample_data import seed_sample_data
from app.models import Base, ForecastSignal, LegislativeBill, OpportunityRecommendation, PolicyAlert, TradeDisclosure
from app.services.alerts import (
    create_alert_subscription,
    deactivate_alert_subscription,
    dispatch_alert,
    get_alert_feed,
    get_alert_subscription_detail,
    list_configured_alert_subscriptions,
    preview_alert_dispatch,
    update_alert_subscription,
)
from app.services.coverage import get_coverage_summary
from app.services.entity_resolution import build_entity_resolution_summary
from app.services.forecasting import build_sector_forecast
from app.services.legislation import get_upcoming_legislation
from app.services.opportunities import get_market_opportunities
from app.schemas.alerts import AlertSubscriptionCreate, AlertSubscriptionUpdate, NotificationChannelConfig\nfrom app.services.portfolio import (
    aggregate_signals,
    detect_conflicts,
    export_conflicts_csv,
    get_member_exposures,
    get_member_trade_history,
    get_portfolio_snapshot,
    get_recent_trade_disclosures,
    get_trade_activity_timeline,
    get_watchlist_summary,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        await seed_sample_data(session, reset=True)
        yield session
    await engine.dispose()


@pytest.mark.anyio
async def test_get_upcoming_legislation_prefers_database(session):
    results = await get_upcoming_legislation(limit=1, session=session)
    assert results[0].bill_id.startswith('LR-')
    assert results[0].jurisdiction == 'Federal'


@pytest.mark.anyio
async def test_build_sector_forecast_prefers_database(session):
    envelope = await build_sector_forecast('Technology', session=session)
    assert envelope.sector == 'Technology'
    assert envelope.signals
    assert 0.0 <= envelope.estimated_accuracy <= 1.0
    assert envelope.methodology_summary
    if envelope.drivers:
        assert isinstance(envelope.drivers[0], str)


@pytest.mark.anyio
async def test_aggregate_signals_group_trades(session):
    signals = await aggregate_signals(limit=2, session=session)
    assert signals
    assert signals[0].supporting_trades


@pytest.mark.anyio
async def test_get_alert_feed_uses_database(session):
    feed = await get_alert_feed(limit=2, session=session)
    assert feed.alerts
    assert feed.alerts[0].id.startswith('alert-')


@pytest.mark.anyio
async def test_get_market_opportunities_uses_database(session):
    payload = await get_market_opportunities(limit=3, session=session)
    assert payload.opportunities
    assert payload.opportunities[0].ticker


@pytest.mark.anyio
async def test_get_coverage_summary_uses_database(session):
    summary = await get_coverage_summary(session=session)
    assert summary.jurisdictions
    assert any(item.name == 'Federal' for item in summary.jurisdictions)
    assert summary.processing_health.ingestion_latency_minutes >= 0


@pytest.mark.anyio
async def test_detect_conflicts_uses_database(session):
    insights = await detect_conflicts(limit=3, session=session)
    assert insights
    assert insights[0].risk_score > 0
    assert insights[0].ticker



@pytest.mark.anyio
async def test_build_entity_resolution_summary(session):
    summary = await build_entity_resolution_summary(session=session)
    assert summary.metrics.total_bills > 0
    assert summary.metrics.coverage_ratio > 0
    assert summary.metrics.coverage_ratio <= 1
    assert any(link.bill_id == 'LR-1000' for link in summary.bill_links)
    lr1000 = next(link for link in summary.bill_links if link.bill_id == 'LR-1000')
    assert 'AIT' in lr1000.tickers
    assert lr1000.coverage_score > 0


@pytest.mark.anyio
async def test_get_portfolio_snapshot_uses_database(session):
    summary = await get_portfolio_snapshot(session=session, lookback_days=60, top_n=3)
    assert summary.total_trades_30d >= 1
    assert summary.top_tickers
    assert summary.top_tickers[0].ticker



@pytest.mark.anyio
async def test_get_trade_activity_timeline(session):
    timeline = await get_trade_activity_timeline(session=session, lookback_days=30)
    assert timeline
    assert timeline[0].total_trades >= 1



@pytest.mark.anyio
async def test_get_member_exposures(session):
    exposures = await get_member_exposures(session=session, lookback_days=60, limit=5)
    assert exposures
    assert exposures[0].total_trades >= 1



@pytest.mark.anyio
async def test_get_member_trade_history(session):
    history = await get_member_trade_history('Sen. Jane Doe', session=session, lookback_days=90, limit=10)
    assert history
    assert history[0].ticker



@pytest.mark.anyio
async def test_get_recent_trade_disclosures(session):
    disclosures = await get_recent_trade_disclosures(limit=3, lookback_days=30, session=session)
    assert disclosures
    first = disclosures[0]
    assert first.ticker
    assert first.transaction_date.tzinfo is not None
    if first.related_bill is not None:
        assert first.related_bill.bill_id






@pytest.mark.anyio
async def test_manage_alert_subscriptions(session):
    payload = AlertSubscriptionCreate(
        subscriber_id='engineer@legaledge.ai',
        label='Engineering high severity',
        categories=['Legislation'],
        entities=['AIT'],
        severities=['High'],
        min_severity='high',
        channels=[NotificationChannelConfig(type='email', target='engineer@legaledge.ai')],
    )
    subscription = await create_alert_subscription(payload, session=session)
    assert subscription.id
    assert subscription.categories == ['legislation']

    scoped = await list_configured_alert_subscriptions(
        session=session, subscriber_id='engineer@legaledge.ai'
    )
    assert any(item.id == subscription.id for item in scoped)

    updated = await update_alert_subscription(
        subscription.id,
        AlertSubscriptionUpdate(entities=['AIT', 'REGN'], min_severity='critical'),
        session=session,
    )
    assert updated.min_severity == 'critical'
    assert 'REGN' in updated.entities

    await deactivate_alert_subscription(subscription.id, session=session)
    detail = await get_alert_subscription_detail(subscription.id, session=session)
    assert detail.is_active is False


@pytest.mark.anyio
async def test_preview_and_dispatch_alerts(session):
    payload = AlertSubscriptionCreate(
        subscriber_id='alerts@legaledge.ai',
        label='Legislation broadcasts',
        categories=['Legislation'],
        entities=['HR-1001'],
        severities=['High'],
        channels=[NotificationChannelConfig(type='email', target='alerts@legaledge.ai')],
    )
    created = await create_alert_subscription(payload, session=session)
    assert created.id

    preview = await preview_alert_dispatch('alert-hr1001', session=session)
    assert preview.targets
    assert any(target.subscription_id == created.id for target in preview.targets)

    dispatch = await dispatch_alert('alert-hr1001', session=session)
    assert dispatch.total_channels == preview.total_channels
    detail = await get_alert_subscription_detail(created.id, session=session)
    assert detail.last_notified_at is not None

@pytest.mark.anyio
async def test_get_watchlist_summary(session):
    summary = await get_watchlist_summary(['AIT', 'GRID'], session=session, lookback_days=60)
    assert summary.entries
    assert summary.total_trades >= 1



@pytest.mark.anyio
async def test_export_conflicts_csv(session):
    csv_output = await export_conflicts_csv(session=session, limit=10)
    assert 'Ticker' in csv_output
    assert 'Risk Score' in csv_output





