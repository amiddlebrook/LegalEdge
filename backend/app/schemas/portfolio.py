"""Portfolio tracker schemas."""
from datetime import datetime

from pydantic import BaseModel


class TradeActivity(BaseModel):
    """Structured view of a congressional trade disclosure."""

    member: str
    chamber: str
    ticker: str
    transaction_type: str
    transaction_date: datetime
    amount_range: str
    related_bill: str | None = None


class PortfolioSignal(BaseModel):
    """Aggregate signal derived from legislative + trading data."""

    ticker: str
    signal: str
    conviction: float
    rationale: str
    supporting_trades: list[TradeActivity]


class ConflictInsight(BaseModel):
    """Potential conflict between a trade and pending legislation."""

    ticker: str
    member: str
    chamber: str
    transaction_type: str
    transaction_date: datetime
    amount_range: str
    bill_id: str | None = None
    bill_title: str | None = None
    bill_stage: str | None = None
    jurisdiction: str | None = None
    next_action_date: datetime | None = None
    risk_score: float
    confidence: float
    rationale: str


