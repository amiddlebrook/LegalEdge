"""Portfolio monitoring service stubs."""
from datetime import datetime, timedelta, timezone

from app.schemas.portfolio import PortfolioSignal, TradeActivity


async def aggregate_signals(limit: int = 5) -> list[PortfolioSignal]:
    """Return deterministic signals for UI scaffolding."""

    base_time = datetime.now(timezone.utc)
    trades = [
        TradeActivity(
            member="Sen. Jane Doe",
            chamber="Senate",
            ticker="AIQ",
            transaction_type="BUY",
            transaction_date=base_time - timedelta(days=3),
            amount_range="$50k-$100k",
            related_bill="S.4242",
        )
    ]

    signals = [
        PortfolioSignal(
            ticker="AIQ",
            signal="Accumulating",
            conviction=0.7,
            rationale="Trading activity aligns with pro-AI procurement bill.",
            supporting_trades=trades,
        ),
        PortfolioSignal(
            ticker="CSPN",
            signal="Watchlist",
            conviction=0.5,
            rationale="House committee hearings may introduce export controls.",
            supporting_trades=[],
        ),
    ]

    return signals[:limit]