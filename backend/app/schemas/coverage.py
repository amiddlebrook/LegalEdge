"""Coverage and ingestion health schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class JurisdictionSnapshot(BaseModel):
    """Roll-up of coverage for a specific jurisdiction."""

    name: str
    bills_monitored: int = Field(ge=0)
    committees_tracked: int = Field(ge=0)
    coverage_ratio: float = Field(ge=0.0, le=1.0)
    last_updated: datetime


class StateProgram(BaseModel):
    """State-level ingestion program status."""

    state: str
    status: Literal['live', 'beta', 'planned']
    last_synced: datetime
    feeds: list[str] = Field(default_factory=list)


class ProcessingHealth(BaseModel):
    """Operational metrics for ingestion and processing pipelines."""

    ingestion_latency_minutes: float = Field(ge=0.0)
    processing_sla_minutes: float = Field(ge=0.0)
    pipelines_active: int = Field(ge=0)
    last_ingestion_run: datetime
    detection_backlog: int = Field(ge=0)


class TradeSurveillanceSummary(BaseModel):
    """Health metrics for congressional trade monitoring."""

    active_watchlist_members: int = Field(ge=0)
    disclosures_last_7_days: int = Field(ge=0)
    conflicts_flagged_last_30_days: int = Field(ge=0)
    high_priority_alerts: int = Field(ge=0)


class CoverageSummary(BaseModel):
    """Composite view of LegalEdge coverage and ingestion posture."""

    generated_at: datetime
    jurisdictions: list[JurisdictionSnapshot]
    state_programs: list[StateProgram]
    processing_health: ProcessingHealth
    trade_surveillance: TradeSurveillanceSummary
    data_sources: list[str] = Field(default_factory=list)
