"""Portfolio monitoring service stubs."""
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.portfolio import list_recent_trades
from app.schemas.portfolio import PortfolioSignal, TradeActivity


async def aggregate_signals(
    limit: int = 5,
    *,
    session: AsyncSession | None = None,
) -> list[PortfolioSignal]:
    """Return portfolio signals backed by trade disclosures when available."""

    if session is not None:
        try:
            disclosures = await list_recent_trades(session, limit=limit * 3)
        except Exception as exc:  # pragma: no cover - defensive log
            logger.warning("Failed to fetch trades from DB: %s", exc)
        else:
            if disclosures:
                logger.debug("Serving %s trades from database", len(disclosures))
                grouped: dict[str, list[TradeActivity]] = defaultdict(list)
                for trade in disclosures:
                    grouped[trade.ticker].append(
                        TradeActivity(
                            member=trade.member,
                            chamber=trade.chamber,
                            ticker=trade.ticker,
                            transaction_type=trade.transaction_type,
                            transaction_date=trade.transaction_date,
                            amount_range=trade.amount_range,
                            related_bill=trade.related_bill,
                        )
                    )

                signals: list[PortfolioSignal] = []
                for ticker, activities in list(grouped.items())[:limit]:
                    buy_count = sum(1 for activity in activities if activity.transaction_type.upper() == "BUY")
                    sell_count = len(activities) - buy_count
                    signal_label = "Accumulating" if buy_count >= sell_count else "Reducing"
                    conviction = min(0.4 + 0.15 * len(activities), 0.9)
                    rationale = (
                        f"{activities[0].member} disclosures indicate {signal_label.lower()} interest "
                        f"around pending legislation."
                    )
                    signals.append(
                        PortfolioSignal(
                            ticker=ticker,
                            signal=signal_label,
                            conviction=conviction,
                            rationale=rationale,
                            supporting_trades=activities,
                        )
                    )

                if signals:
                    return signals

    logger.debug("Falling back to stubbed portfolio signals")
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