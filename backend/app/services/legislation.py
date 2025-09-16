"""Legislative data ingestion and feature services."""
from datetime import date, datetime, timedelta, timezone
from typing import Iterable

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.legislation import list_upcoming_legislation as repo_list_upcoming_legislation
from app.schemas.legislation import BillImpactProjection, BillImpactRequest, LegislativeBrief


async def get_upcoming_legislation(
    limit: int = 10,
    *,
    session: AsyncSession | None = None,
) -> list[LegislativeBrief]:
    """Return normalized legislative records sourced from the database when available."""

    if session is not None:
        try:
            db_records = await repo_list_upcoming_legislation(session, limit=limit)
        except Exception as exc:  # pragma: no cover - defensive log
            logger.warning("Failed to fetch legislation from DB: %s", exc)
        else:
            if db_records:
                logger.debug("Serving %s bills from database", len(db_records))
                return [_bill_to_schema(bill) for bill in db_records]

    logger.debug("Falling back to stubbed legislation data")
    return list(_stub_legislation(limit))


async def analyze_legislation(request: BillImpactRequest) -> BillImpactProjection:
    """Placeholder AI analysis result."""

    movement = {ticker: 0.05 for ticker in request.target_tickers}
    return BillImpactProjection(
        bill_id=request.bill_id,
        impacted_tickers=request.target_tickers,
        projected_movement=movement,
        confidence=0.62,
        narrative=(
            "Pending compliance costs could pressure margins in the short term, "
            "but boosts to data governance providers create upside scenarios."
        ),
    )


def _bill_to_schema(bill) -> LegislativeBrief:
    return LegislativeBrief(
        bill_id=bill.bill_id,
        title=bill.title,
        stage=bill.stage,
        jurisdiction=bill.jurisdiction,
        committees=list(bill.committees or []),
        sectors=list(bill.sectors or []),
        summary=bill.summary,
        next_action_date=bill.next_action_date,
        sentiment_score=bill.sentiment_score,
        probability_of_enactment=bill.probability_of_enactment,
        last_updated=bill.last_updated,
    )


def _stub_legislation(limit: int) -> Iterable[LegislativeBrief]:
    now = datetime.now(timezone.utc)
    for idx in range(limit):
        yield LegislativeBrief(
            bill_id=f"HR-10{idx}",
            title="AI Accountability and Transparency Act",
            stage="Committee",
            jurisdiction="Federal",
            committees=["House Energy & Commerce"],
            sectors=["Technology", "Financial Services"],
            summary="Establishes reporting standards for AI-driven trading systems.",
            next_action_date=date.today() + timedelta(days=14 + idx),
            sentiment_score=0.42,
            probability_of_enactment=0.31,
            last_updated=now,
        )