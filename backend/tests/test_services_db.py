import pytest
import pytest_asyncio
from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import Base, ForecastSignal, LegislativeBill, TradeDisclosure
from app.services.forecasting import build_sector_forecast
from app.services.legislation import get_upcoming_legislation
from app.services.portfolio import aggregate_signals


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        yield session
    await engine.dispose()


@pytest.mark.anyio
async def test_get_upcoming_legislation_prefers_database(session):
    bill = LegislativeBill(
        bill_id="TEST-1",
        title="Data Privacy Modernization Act",
        stage="Hearing",
        jurisdiction="Federal",
        committees=["House Judiciary"],
        sectors=["Technology"],
        summary="Modernizes privacy requirements for AI systems.",
        next_action_date=date.today(),
        sentiment_score=0.65,
        probability_of_enactment=0.52,
        last_updated=datetime.now(timezone.utc),
    )
    session.add(bill)
    await session.commit()

    results = await get_upcoming_legislation(limit=1, session=session)

    assert results[0].bill_id == "TEST-1"
    assert results[0].jurisdiction == "Federal"


@pytest.mark.anyio
async def test_build_sector_forecast_prefers_database(session):
    forecast = ForecastSignal(
        sector="Technology",
        ticker="AIT",
        thesis="Public sector AI procurement drives revenue.",
        expected_return_pct=7.5,
        confidence=0.72,
        catalysts=["Federal procurement mandate"],
        horizon_days=45,
        generated_on=date.today(),
    )
    session.add(forecast)
    await session.commit()

    envelope = await build_sector_forecast("Technology", session=session)

    assert any(signal.ticker == "AIT" for signal in envelope.signals)
    assert envelope.generated_on == forecast.generated_on


@pytest.mark.anyio
async def test_aggregate_signals_group_trades(session):
    trade = TradeDisclosure(
        member="Rep. Alex Smith",
        chamber="House",
        ticker="AIF",
        transaction_type="BUY",
        transaction_date=datetime.now(timezone.utc),
        amount_range="$15k-$50k",
        related_bill="HR-2042",
    )
    session.add(trade)
    await session.commit()

    signals = await aggregate_signals(limit=2, session=session)

    assert signals
    assert signals[0].supporting_trades
    assert signals[0].supporting_trades[0].ticker == "AIF"