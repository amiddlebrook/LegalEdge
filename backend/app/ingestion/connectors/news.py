"""News and RSS connector."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

from app.ingestion.connectors.base import BasePollingConnector
from app.schemas.ingestion import IngestionArtifact


class NewsRssConnector(BasePollingConnector):
    source_name = 'news.rss'
    poll_interval_seconds = 180.0
    calls_per_minute = 12

    async def _fetch(self) -> Iterable[IngestionArtifact]:
        now = datetime.now(timezone.utc)
        return [
            IngestionArtifact(
                source=self.source_name,
                external_id='policywire-ait-2025-09-17',
                jurisdiction='Federal',
                title='OMB releases AI procurement modernization roadmap',
                summary='Roadmap aligns federal procurement with AI accountability mandates.',
                stage=None,
                introduced_at=None,
                last_updated=now,
                committees=['Office of Management and Budget'],
                sectors=['Technology'],
                entities=['AIT'],
                metadata={'publisher': 'PolicyWire', 'url': 'https://policywire.example/ait-ai-modernization'},
            ),
            IngestionArtifact(
                source=self.source_name,
                external_id='energywatch-grid-2025-09-17',
                jurisdiction='Texas',
                title='Texas commission fast-tracks grid resilience grants',
                summary='Public Utility Commission accelerates grants tied to SB-88 implementation.',
                stage=None,
                introduced_at=None,
                last_updated=now - timedelta(minutes=5),
                committees=['Public Utility Commission of Texas'],
                sectors=['Energy', 'Utilities'],
                entities=['GRID'],
                metadata={'publisher': 'EnergyWatch', 'url': 'https://energywatch.example/grid-grants'},
            ),
        ]


__all__ = ['NewsRssConnector']
