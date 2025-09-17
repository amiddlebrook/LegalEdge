import pytest
import pytest_asyncio
from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.ingestion.sample_data import seed_sample_data
from app.models import Base, ForecastSignal, LegislativeBill, OpportunityRecommendation, PolicyAlert, TradeDisclosure
from app.services.alerts import get_alert_feed
from app.services.coverage import get_coverage_summary
from app.services.entity_resolution import build_entity_resolution_summary
from app.services.forecasting import build_sector_forecast
from app.services.legislation import get_upcoming_legislation
from app.services.opportunities import get_market_opportunities
from app.services.portfolio import aggregate_signals, detect_conflicts, get_portfolio_snapshot


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
