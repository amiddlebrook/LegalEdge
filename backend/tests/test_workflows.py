import pytest
import pytest_asyncio
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import Base, LegislativeBill
from app.workflows.pipeline import run_daily_ingestion


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def session_factory():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    # Seed minimal bill to ensure query hits persisted data
    async with factory() as session:
        session.add(
            LegislativeBill(
                bill_id='TEST-INGEST',
                title='Development Oversight Act',
                stage='Introduced',
                jurisdiction='Federal',
                committees=['House Oversight'],
                sectors=['Technology'],
                summary='Ensures ingestion pipeline sanity.',
                next_action_date=datetime.now(timezone.utc).date(),
                sentiment_score=0.5,
                probability_of_enactment=0.2,
                last_updated=datetime.now(timezone.utc),
            )
        )
        await session.commit()

    yield factory
    await engine.dispose()


@pytest.mark.anyio
async def test_run_daily_ingestion_uses_session_factory(session_factory):
    # Should not raise when a session factory is provided
    await run_daily_ingestion(session_factory=session_factory)