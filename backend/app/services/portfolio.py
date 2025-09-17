"""Portfolio monitoring service stubs."""
from collections import defaultdict
from datetime import datetime, timedelta, timezone, time as dtime

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legislation import LegislativeBill
from app.models.portfolio import TradeDisclosure
from app.repositories.portfolio import list_recent_trades
from app.schemas.portfolio import ConflictInsight, PortfolioSignal, TradeActivity


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

async def detect_conflicts(
    limit: int = 5,
    *,
    session: AsyncSession | None = None,
) -> list[ConflictInsight]:
    """Identify potential conflicts between congressional trades and pending legislation."""

    async def _resolve_bills(bill_ids: set[str]) -> dict[str, LegislativeBill]:
        if not bill_ids:
            return {}
        try:
            stmt = select(LegislativeBill).where(LegislativeBill.bill_id.in_(bill_ids))
            result = await session.execute(stmt)
            return {bill.bill_id: bill for bill in result.scalars().all()}
        except Exception as exc:  # pragma: no cover - defensive log
            logger.warning('Failed to resolve bills for conflicts: %s', exc)
            return {}

    def _build_insights(
        trades: list[TradeDisclosure],
        bills: dict[str, LegislativeBill],
    ) -> list[ConflictInsight]:
        insights: list[ConflictInsight] = []
        for trade in trades:
            bill = bills.get(trade.related_bill) if trade.related_bill else None
            risk, confidence, rationale = _score_conflict(trade, bill)
            next_action = None
            if bill and bill.next_action_date:
                next_action = datetime.combine(bill.next_action_date, dtime.min).replace(tzinfo=timezone.utc)
            insights.append(
                ConflictInsight(
                    ticker=trade.ticker,
                    member=trade.member,
                    chamber=trade.chamber,
                    transaction_type=trade.transaction_type,
                    transaction_date=_ensure_timezone(trade.transaction_date),
                    amount_range=trade.amount_range,
                    bill_id=bill.bill_id if bill else trade.related_bill,
                    bill_title=bill.title if bill else None,
                    bill_stage=bill.stage if bill else None,
                    jurisdiction=bill.jurisdiction if bill else None,
                    next_action_date=next_action,
                    risk_score=round(risk, 3),
                    confidence=round(confidence, 3),
                    rationale=rationale,
                )
            )
        insights.sort(key=lambda item: item.risk_score, reverse=True)
        return insights[:limit]

    if session is not None:
        try:
            disclosures = await list_recent_trades(session, limit=limit * 4)
        except Exception as exc:  # pragma: no cover - defensive log
            logger.warning('Failed to query trades for conflicts: %s', exc)
        else:
            if disclosures:
                bill_map = await _resolve_bills({trade.related_bill for trade in disclosures if trade.related_bill})
                insights = _build_insights(disclosures, bill_map)
                if insights:
                    return insights

    logger.debug('Falling back to stubbed conflict insights')
    now = datetime.now(timezone.utc)
    return [
        ConflictInsight(
            ticker='AIT',
            member='Sen. Jane Doe',
            chamber='Senate',
            transaction_type='BUY',
            transaction_date=now - timedelta(days=2),
            amount_range='-',
            bill_id='LR-1000',
            bill_title='AI Accountability and Transparency Act',
            bill_stage='Committee',
            jurisdiction='Federal',
            next_action_date=now + timedelta(days=10),
            risk_score=0.72,
            confidence=0.65,
            rationale='Buy disclosures align with AI accountability markup advancing in committee.',
        ),
        ConflictInsight(
            ticker='REGN',
            member='Rep. Alex Smith',
            chamber='House',
            transaction_type='BUY',
            transaction_date=now - timedelta(days=1, hours=4),
            amount_range='-',
            bill_id='CA-AB-452',
            bill_title='California Algorithmic Accountability Framework',
            bill_stage='Assembly',
            jurisdiction='California',
            next_action_date=now + timedelta(days=6),
            risk_score=0.64,
            confidence=0.58,
            rationale='State algorithmic accountability expansion overlaps with ongoing REGN accumulation.',
        ),
    ][:limit]


def _ensure_timezone(value: datetime) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _score_conflict(trade: TradeDisclosure, bill: LegislativeBill | None) -> tuple[float, float, str]:
    base = 0.45 if trade.transaction_type.upper() == 'BUY' else 0.4
    if bill is None:
        rationale = (
            f"{trade.member} disclosure lacks linked legislation but may warrant manual review."
        )
        return base, 0.4, rationale

    stage_weights = {
        'introduced': 0.35,
        'committee': 0.45,
        'floor': 0.55,
        'enacted': 0.7,
        'passed': 0.65,
    }
    stage_label = bill.stage or 'Pending'
    stage_key = stage_label.lower()
    stage_weight = stage_weights.get(stage_key, 0.4)
    probability = bill.probability_of_enactment or 0.3
    sentiment = bill.sentiment_score or 0.5
    exposure = 0.05 * len(bill.sectors or [])

    risk = min(1.0, base + stage_weight * 0.4 + probability * 0.35 + sentiment * 0.15 + exposure)
    confidence = min(1.0, 0.45 + probability * 0.4 + stage_weight * 0.1)
    stage_phrase = stage_label.lower()
    rationale = (
        f"{trade.member} {trade.transaction_type.lower()} disclosure overlaps with {stage_phrase} action on {bill.title}."
    )
    return risk, confidence, rationale

