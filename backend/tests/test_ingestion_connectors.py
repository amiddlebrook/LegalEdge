import pytest

from app.ingestion.connectors import (
    CongressGovConnector,
    NewsRssConnector,
    SecFilingsConnector,
    StatePortalConnector,
)
from app.ingestion.manager import IngestionManager, group_artifacts_by_jurisdiction
from app.ingestion.registry import get_default_connectors


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.mark.anyio
async def test_congress_connector_emits_artifacts():
    connector = CongressGovConnector()
    batch = await connector.poll()
    assert batch
    assert all(item.source == 'congress.gov' for item in batch)


@pytest.mark.anyio
async def test_state_and_sec_connectors_return_unique_ids():
    state_batch = await StatePortalConnector().poll()
    sec_batch = await SecFilingsConnector().poll()
    state_ids = {item.external_id for item in state_batch}
    sec_ids = {item.external_id for item in sec_batch}
    assert state_ids
    assert sec_ids
    assert state_ids.isdisjoint(sec_ids)


@pytest.mark.anyio
async def test_ingestion_manager_deduplicates_across_connectors():
    manager = IngestionManager(get_default_connectors())
    first_count = await manager.poll_once()
    assert first_count > 0
    second_count = await manager.poll_once()
    assert second_count == 0

    batches = await manager.drain_batches()
    assert batches
    total_artifacts = sum(len(batch.artifacts) for batch in batches)
    assert total_artifacts == first_count

    buckets = group_artifacts_by_jurisdiction(
        [artifact for batch in batches for artifact in batch.artifacts]
    )
    assert 'Federal' in buckets
