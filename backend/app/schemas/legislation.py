"""Pydantic models for legislative data."""
from datetime import date, datetime

from pydantic import BaseModel, Field, HttpUrl


class LegislativeSource(BaseModel):
    """Metadata about a primary data source."""

    name: str
    url: HttpUrl
    refresh_interval_minutes: int


class LegislativeBrief(BaseModel):
    """Summarized view of a bill or regulatory proposal."""

    bill_id: str
    title: str
    stage: str
    jurisdiction: str
    committees: list[str]
    sectors: list[str]
    summary: str
    next_action_date: date | None = None
    sentiment_score: float | None = None
    probability_of_enactment: float | None = None
    last_updated: datetime


class BillImpactRequest(BaseModel):
    """Request payload for AI-driven impact analysis."""

    bill_id: str
    full_text_url: HttpUrl | None = None
    synopsis: str
    target_tickers: list[str]
    risk_appetite: str = "balanced"


class BillImpactProjection(BaseModel):
    """Model response for a predicted market impact."""

    bill_id: str
    impacted_tickers: list[str]
    projected_movement: dict[str, float]
    confidence: float
    narrative: str
    sentiment_score: float
    enactment_probability: float
    sector_impacts: dict[str, float] | None = None
    model_version: str | None = None
    drivers: list[str] = Field(default_factory=list)
    diagnostics: dict[str, object] | None = None
