"""Market opportunity schemas."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class OpportunityRecommendation(BaseModel):
    """Actionable investment opportunity derived from policy signals."""

    ticker: str
    thesis: str
    expected_return_pct: float
    conviction: float
    horizon_days: int
    catalysts: list[str]
    risk_rating: str
    policy_alignment: float | None = None
    policy_alpha: float | None = None
    conflict_score: float | None = None
    composite_score: float | None = None
    drivers: list[str] | None = None
    conflict_insights: list[str] | None = None
    explanation: str | None = None
    methodology: str | None = None


class OpportunityPayload(BaseModel):
    """Collection of opportunity recommendations."""

    generated_at: datetime
    opportunities: list[OpportunityRecommendation]
    applied_filters: dict[str, Any] | None = None
    ranker_version: str | None = None
    scoring_notes: str | None = None
    top_drivers: list[str] | None = None
