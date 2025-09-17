import pytest
import pytest_asyncio
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import select

from app.ingestion.persistence import NormalizationSummary, persist_artifacts, persist_batches
from app.models import Base, LegislativeBill, LegislativeBillVersion
from app.schemas.ingestion import IngestionArtifact, IngestionBatch


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


def _make_artifact(**overrides):
    base = {
        'artifact_type': 'legislation',
        'source': 'congress.gov',
        'external_id': 'hr-8890',
        'jurisdiction': 'Federal',
        'title': 'AI Governance Accountability Act',
        'summary': 'Mandates algorithmic transparency reviews.',
        'stage': 'Committee',
        'introduced_at': datetime.now(timezone.utc),
        'last_updated': datetime.now(timezone.utc),
        'committees': ['House Energy & Commerce'],
        'sectors': ['Technology'],
        'entities': ['AIT'],
        'metadata': {},
    }
    base.update(overrides)
    return IngestionArtifact(**base)


@pytest.mark.anyio
async def test_persist_artifacts_creates_new_bill(session):
    artifact = _make_artifact()

    summary = await persist_artifacts([artifact], session=session)

    assert isinstance(summary, NormalizationSummary)
    assert summary.created == 1
    assert summary.versions_created == 1

    result = await session.execute(select(LegislativeBill).where(LegislativeBill.bill_id == 'HR-8890'))
    bill = result.scalar_one()
    assert bill.summary.startswith('Mandates')

    versions = await session.execute(select(LegislativeBillVersion).where(LegislativeBillVersion.bill_id == 'HR-8890'))
    assert versions.scalars().one().version == 1


@pytest.mark.anyio
async def test_persist_artifacts_updates_existing_bill(session):
    artifact = _make_artifact()
    await persist_artifacts([artifact], session=session)

    updated = _make_artifact(summary='Updated transparency mandate summary.', stage='Floor')
    summary = await persist_artifacts([updated], session=session)

    assert summary.created == 0
    assert summary.updated == 1
    assert summary.skipped == 0
    assert summary.versions_created == 1

    result = await session.execute(select(LegislativeBill).where(LegislativeBill.bill_id == 'HR-8890'))
    bill = result.scalar_one()
    assert bill.stage == 'Floor'
    assert 'Updated transparency' in bill.summary

    versions = await session.execute(select(LegislativeBillVersion).where(LegislativeBillVersion.bill_id == 'HR-8890').order_by(LegislativeBillVersion.version))
    version_numbers = [row.version for row in versions.scalars().all()]
    assert version_numbers == [1, 2]


@pytest.mark.anyio
async def test_persist_batches_skips_non_legislative(session):
    artifact = _make_artifact(artifact_type='news', source='news.rss', external_id='breaking-ait', summary='News item')
    batch = IngestionBatch(source='news.rss', pulled_at=datetime.now(timezone.utc), artifacts=[artifact])

    summary = await persist_batches([batch], session=session)

    assert summary.legislation_processed == 0
    assert summary.total_persisted == 0
