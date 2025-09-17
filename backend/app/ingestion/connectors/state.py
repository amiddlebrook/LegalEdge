"""State legislature connector."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

from app.ingestion.connectors.base import BasePollingConnector
from app.schemas.ingestion import IngestionArtifact


class StatePortalConnector(BasePollingConnector):
    source_name = 'state_portal'
    poll_interval_seconds = 600.0
    calls_per_minute = 4

    async def _fetch(self) -> Iterable[IngestionArtifact]:
        now = datetime.now(timezone.utc)
        return [
            IngestionArtifact(
                source=self.source_name,
                external_id='ca-ab-452',
                jurisdiction='California',
                title='California Privacy Modernization Act',
                summary='Expands consumer privacy guardrails for AI-enabled services.',
                stage='Hearing Scheduled',
                introduced_at=now - timedelta(days=12),
                last_updated=now,
                committees=['Assembly Privacy & Consumer Protection'],
                sectors=['Technology', 'Consumer'],
                entities=['REGN'],
                metadata={'hearing_date': (now + timedelta(days=4)).isoformat()},
            ),
            IngestionArtifact(
                source=self.source_name,
                external_id='tx-sb-88',
                jurisdiction='Texas',
                title='Texas Grid Resilience Modernization',
                summary='Allocates funding for distributed energy resources and grid security.',
                stage='Floor',
                introduced_at=now - timedelta(days=20),
                last_updated=now,
                committees=['Senate Business & Commerce'],
                sectors=['Energy', 'Utilities'],
                entities=['GRID'],
                metadata={'sponsor_party': 'Nonpartisan Caucus'},
            ),
        ]


__all__ = ['StatePortalConnector']
