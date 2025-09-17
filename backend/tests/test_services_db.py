import pytest
import pytest_asyncio
from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.ingestion.sample_data import seed_sample_data
from app.models import Base, ForecastSignal, LegislativeBill, OpportunityRecommendation, PolicyAlert, TradeDisclosure
from app.services.alerts import get_alert_feed
from app.services.forecasting import build_sector_forecast
from app.services.legislation import get_upcoming_legislation
from app.services.opportunities import get_market_opportunities
from app.services.portfolio import aggregate_signals


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