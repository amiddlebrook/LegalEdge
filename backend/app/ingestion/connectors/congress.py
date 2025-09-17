"""Connector for congress.gov."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

from app.ingestion.connectors.base import BasePollingConnector
from app.schemas.ingestion import IngestionArtifact


class CongressGovConnector(BasePollingConnector):
    source_name = 'congress.gov'
    poll_interval_seconds = 300.0
    calls_per_minute = 6

    async def _fetch(self) -> Iterable[IngestionArtifact]:
        now = datetime.now(timezone.utc)
        return [
            IngestionArtifact(
                source=self.source_name,
                external_id='hr-8890',
                jurisdiction='Federal',
                title='AI Governance Accountability Act of 2025',
                summary='Mandates algorithmic transparency reviews for federal contractors.',
                stage='Committee',
                introduced_at=now - timedelta(days=5),
                last_updated=now,
                committees=['House Energy & Commerce'],
                sectors=['Technology', 'Defense'],
                entities=['AIT'],
                metadata={'chamber': 'House', 'sponsor': 'Rep. Alex Smith'},
            ),
            IngestionArtifact(
                source=self.source_name,
                external_id='s-3241',
                jurisdiction='Federal',
                title='Critical Infrastructure Resilience Modernization Act',
                summary='Expands resilient grid funding and cybersecurity oversight for utilities.',
                stage='Introduced',
                introduced_at=now - timedelta(days=3),
                last_updated=now,
                committees=['Senate Energy & Natural Resources'],
                sectors=['Energy', 'Utilities'],
                entities=['GRID'],
                metadata={'chamber': 'Senate', 'sponsor': 'Sen. Malik Johnson'},
            ),
        ]


__all__ = ['CongressGovConnector']
