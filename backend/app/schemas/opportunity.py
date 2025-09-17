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


class OpportunityPayload(BaseModel):
    """Collection of opportunity recommendations."""

    generated_at: datetime
    opportunities: list[OpportunityRecommendation]
    applied_filters: dict[str, Any] | None = None
