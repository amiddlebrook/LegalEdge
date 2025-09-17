"""Entity resolution schemas."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.common import TimeStampedModel


class EntityEvidence(BaseModel):
    """Evidence supporting a link between a bill and a market entity."""

    source: Literal['trade', 'forecast', 'opportunity']
    ticker: str
    description: str
    weight: float | None = Field(default=None, ge=0.0, le=1.0)
    metadata: dict[str, Any] | None = None


class BillEntityLink(BaseModel):
    """Normalized view of a bill and its linked market entities."""

    bill_id: str
    title: str
    jurisdiction: str
    committees: list[str]
    sectors: list[str]
    tickers: list[str]
    evidence: list[EntityEvidence]
    coverage_score: float = Field(ge=0.0, le=1.0)


class ResolutionMetrics(BaseModel):
    """Aggregate coverage metrics for the entity resolution system."""

    total_bills: int
    bills_with_tickers: int
    coverage_ratio: float = Field(ge=0.0, le=1.0)
    average_tickers_per_bill: float
    tracked_committees: int
    orphan_bills: list[str]


class TickerInsight(BaseModel):
    """Insight into how frequently a ticker is linked across bills."""

    ticker: str
    link_count: int
    linked_bills: list[str]
    sectors: list[str]


class EntityResolutionSummary(TimeStampedModel):
    """Full snapshot of LegalEdge entity resolution coverage."""

    metrics: ResolutionMetrics
    bill_links: list[BillEntityLink]
    top_entities: list[TickerInsight]


__all__ = [
    'BillEntityLink',
    'EntityEvidence',
    'EntityResolutionSummary',
    'ResolutionMetrics',
    'TickerInsight',
]
