"""Ingestion manager orchestrating connector polling."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Iterable, Sequence

from loguru import logger

from app.ingestion.connectors import BasePollingConnector
from app.schemas.ingestion import IngestionArtifact, IngestionBatch


class IngestionManager:
    """Coordinate polling across connectors and queue artifacts."""

    def __init__(
        self,
        connectors: Sequence[BasePollingConnector],
        *,
        queue: asyncio.Queue[tuple[str, IngestionArtifact]] | None = None,
    ) -> None:
        self._connectors = list(connectors)
        self._queue: asyncio.Queue[tuple[str, IngestionArtifact]] = queue or asyncio.Queue()
        self._seen: set[tuple[str, str]] = set()

    @property
    def connectors(self) -> Sequence[BasePollingConnector]:
        return tuple(self._connectors)

    async def poll_once(self) -> int:
        """Poll each connector once and enqueue unique artifacts."""

        enqueued = 0
        for connector in self._connectors:
            batch = await connector.poll()
            if not batch:
                continue

            logger.debug('Connector %s returned %s artifacts', connector.source_name, len(batch))
            for artifact in batch:
                key = (artifact.source, artifact.external_id)
                if key in self._seen:
                    continue
                self._seen.add(key)
                await self._queue.put((connector.source_name, artifact))
                enqueued += 1
        return enqueued

    async def drain_batches(self) -> list[IngestionBatch]:
        """Drain the queue into batches grouped by source."""

        grouped: dict[str, list[IngestionArtifact]] = {}
        while not self._queue.empty():
            source, artifact = await self._queue.get()
            grouped.setdefault(source, []).append(artifact)
            self._queue.task_done()

        batches = [
            IngestionBatch(source=source, pulled_at=datetime.now(timezone.utc), artifacts=artifacts)
            for source, artifacts in grouped.items()
        ]
        batches.sort(key=lambda item: item.source)
        return batches

    def reset_seen(self) -> None:
        """Clear deduplication state (useful for tests or manual overrides)."""

        self._seen.clear()


def group_artifacts_by_jurisdiction(artifacts: Iterable[IngestionArtifact]) -> dict[str, list[IngestionArtifact]]:
    """Utility to bucket artifacts by jurisdiction for downstream handling."""

    buckets: dict[str, list[IngestionArtifact]] = {}
    for artifact in artifacts:
        buckets.setdefault(artifact.jurisdiction, []).append(artifact)
    return buckets


__all__ = ['IngestionManager', 'group_artifacts_by_jurisdiction']
