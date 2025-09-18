import pytest
import pytest_asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.ml.forecaster import Forecaster
from app.ml.legislation_pipeline import LegislationNlpPipeline
from app.models import Base, LegislativeBill, LegislativeBillVersion
from app.workflows import pipeline as workflows_pipeline
from app.workflows.pipeline import retrain_forecasting_models, retrain_legislation_models, run_daily_ingestion


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
    await run_daily_ingestion(session_factory=session_factory)

    async with session_factory() as session:
        result = await session.execute(
            select(LegislativeBill).where(LegislativeBill.bill_id == 'HR-8890')
        )
        bill = result.scalar_one_or_none()
        assert bill is not None

        versions = await session.execute(
            select(LegislativeBillVersion).where(
                LegislativeBillVersion.bill_id == 'HR-8890'
            )
        )
        assert versions.scalars().all()


@pytest.mark.anyio
async def test_retrain_legislation_models(monkeypatch):
    pipeline = LegislationNlpPipeline(enable_transformers=False)
    monkeypatch.setattr(pipeline, '_stamp_version', lambda: 'v0')
    await pipeline.retrain()
    assert pipeline._model_version == 'v0'

    monkeypatch.setattr(pipeline, '_stamp_version', lambda: 'v1')
    monkeypatch.setattr(workflows_pipeline, 'get_pipeline', lambda: pipeline)
    await retrain_legislation_models()
    assert pipeline._model_version == 'v1'


@pytest.mark.anyio
async def test_retrain_forecasting_models(monkeypatch):
    forecaster = Forecaster()
    called = {}

    async def fake_retrain():
        called['done'] = True

    monkeypatch.setattr(forecaster, 'retrain', fake_retrain)
    monkeypatch.setattr(workflows_pipeline, 'get_forecaster', lambda: forecaster)

    await retrain_forecasting_models()
    assert called['done'] is True
