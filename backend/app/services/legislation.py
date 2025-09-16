"""Legislative data ingestion and feature stubs."""
from datetime import date, datetime, timedelta

from app.schemas.legislation import BillImpactProjection, BillImpactRequest, LegislativeBrief


async def get_upcoming_legislation(limit: int = 10) -> list[LegislativeBrief]:
    """Return mock legislative records until data pipelines are wired."""

    now = datetime.utcnow()
    records: list[LegislativeBrief] = []
    for idx in range(limit):
        records.append(
            LegislativeBrief(
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
        )
    return records


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