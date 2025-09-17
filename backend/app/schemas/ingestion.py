"""Schemas for ingestion connectors."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class IngestionArtifact(BaseModel):
    """Normalized artifact emitted by ingestion connectors."""

    artifact_type: Literal['legislation', 'filing', 'news'] | str
    source: Literal['congress.gov', 'state_portal', 'sec.filings', 'news.rss'] | str
    external_id: str
    jurisdiction: str
    title: str
    summary: str
    stage: str | None = None
    introduced_at: datetime | None = None
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    committees: list[str] = Field(default_factory=list)
    sectors: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestionBatch(BaseModel):
    """Envelope returned by ingestion manager when draining queue."""

    source: str
    pulled_at: datetime
    artifacts: list[IngestionArtifact]


__all__ = ['IngestionArtifact', 'IngestionBatch']
