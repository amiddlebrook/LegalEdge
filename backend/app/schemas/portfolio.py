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

class TradeTimelinePoint(BaseModel):
    """Aggregated activity metrics for a specific day."""

    date: datetime
    total_trades: int
    buy_count: int
    sell_count: int
    tickers: dict[str, int]


class TickerDrilldown(BaseModel):
    """Aggregated activity metrics for a ticker."""

    ticker: str
    total_trades: int
    buy_count: int
    sell_count: int
    net_flow: str
    members: list[str]
    chambers: list[str]
    last_trade_at: datetime


class PortfolioSnapshot(BaseModel):
    """Overview of recent congressional trading activity."""

    generated_at: datetime
    total_trades_30d: int
    unique_members: int
    unique_tickers: int
    filings_last_7d: int
    buy_sell_ratio: float | None
    top_tickers: list[TickerDrilldown]

