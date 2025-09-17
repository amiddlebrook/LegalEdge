import pytest
import pytest_asyncio
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.ingestion.sample_data import seed_sample_data
from app.models import Base, ForecastSignal, LegislativeBill, TradeDisclosure


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
        yield session
    await engine.dispose()


@pytest.mark.anyio
async def test_seed_sample_data_populates_tables(session):
    await seed_sample_data(session, reset=True)

    bills = await session.execute(select(LegislativeBill))
    forecasts = await session.execute(select(ForecastSignal))
    trades = await session.execute(select(TradeDisclosure))

    assert len(bills.scalars().all()) >= 3
    assert len(forecasts.scalars().all()) >= 3
    assert len(trades.scalars().all()) >= 3