"""Connector registry for LegalEdge ingestion."""
from __future__ import annotations

from typing import Sequence

from app.ingestion.connectors import (
    CongressGovConnector,
    NewsRssConnector,
    SecFilingsConnector,
    StatePortalConnector,
)
from app.ingestion.connectors.base import BasePollingConnector


def get_default_connectors() -> Sequence[BasePollingConnector]:
    """Instantiate the default suite of ingestion connectors."""

    return (
        CongressGovConnector(),
        StatePortalConnector(),
        SecFilingsConnector(),
        NewsRssConnector(),
    )


__all__ = ['get_default_connectors']
