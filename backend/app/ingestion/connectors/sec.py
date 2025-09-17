"""SEC filings connector."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

from app.ingestion.connectors.base import BasePollingConnector
from app.schemas.ingestion import IngestionArtifact


class SecFilingsConnector(BasePollingConnector):
    source_name = 'sec.filings'
    poll_interval_seconds = 900.0
    calls_per_minute = 3

    async def _fetch(self) -> Iterable[IngestionArtifact]:
        now = datetime.now(timezone.utc)
        return [
            IngestionArtifact(
                source=self.source_name,
                external_id='0001181431-25-000123',
                jurisdiction='Federal',
                title='Form 4 - Sen. Jane Doe - AIT',
                summary='Form 4 disclosure indicating continued accumulation of AIT.',
                stage=None,
                introduced_at=now - timedelta(days=1),
                last_updated=now,
                committees=['Senate Armed Services'],
                sectors=['Technology'],
                entities=['AIT'],
                metadata={'filing_type': 'Form 4', 'transaction_type': 'BUY'},
            ),
            IngestionArtifact(
                source=self.source_name,
                external_id='0000899243-25-000045',
                jurisdiction='Federal',
                title='Schedule 13D - GRID Strategic Investors',
                summary='Consortium reports 7.5% position in GRID citing critical infrastructure prospects.',
                stage=None,
                introduced_at=now - timedelta(days=2),
                last_updated=now,
                committees=[],
                sectors=['Energy', 'Utilities'],
                entities=['GRID'],
                metadata={'filing_type': 'Schedule 13D', 'beneficial_owner': 'GRID Strategic Investors LLC'},
            ),
        ]


__all__ = ['SecFilingsConnector']
