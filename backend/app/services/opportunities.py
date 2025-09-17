"""Opportunity recommendation services."""
from datetime import datetime, timezone
from typing import Iterable

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.insights import list_opportunities
from app.schemas.opportunity import OpportunityPayload, OpportunityRecommendation


_ALLOWED_RISK_RATINGS = {
    'low',
    'balanced',
    'medium',
    'high',
}


def _normalize_risk_filters(values: Iterable[str] | None) -> list[str] | None:
    if not values:
        return None
    normalized = [value.lower() for value in values if value and value.lower() in _ALLOWED_RISK_RATINGS]
    return normalized or None


async def get_market_opportunities(
    limit: int = 5,
    *,
    session: AsyncSession | None = None,
    risk_ratings: list[str] | None = None,
    min_conviction: float | None = None,
    max_horizon_days: int | None = None,
) -> OpportunityPayload:
    logger.debug('Generating %s market opportunities', limit)
    """Return opportunity recommendations seeded in the database when available."""

    normalized_risks = _normalize_risk_filters(risk_ratings)

    if session is not None:
        try:
            opportunities = await list_opportunities(
                session,
                limit=limit,
                risk_ratings=normalized_risks,
                min_conviction=min_conviction,
                max_horizon_days=max_horizon_days,
            )
        except Exception as exc:  # pragma: no cover - defensive log
            logger.warning('Failed to fetch opportunities from DB: %s', exc)
        else:
            if opportunities:
                generated_at = opportunities[0].updated_at or opportunities[0].created_at
                return OpportunityPayload(
                    generated_at=generated_at,
                    opportunities=[
                        OpportunityRecommendation(
                            ticker=item.ticker,
                            thesis=item.thesis,
                            expected_return_pct=item.expected_return_pct,
                            conviction=item.conviction,
                            horizon_days=item.horizon_days,
                            catalysts=list(item.catalysts or []),
                            risk_rating=item.risk_rating,
                        )
                        for item in opportunities
                    ],
                    applied_filters=_build_applied_filters(
                        risk_ratings, min_conviction, max_horizon_days
                    ),
                )

    return _fallback_payload(
        limit=limit,
        risk_ratings=normalized_risks,
        min_conviction=min_conviction,
        max_horizon_days=max_horizon_days,
    )


def _fallback_payload(
    *,
    limit: int,
    risk_ratings: list[str] | None,
    min_conviction: float | None,
    max_horizon_days: int | None,
) -> OpportunityPayload:
    generated_at = datetime.now(timezone.utc)
    recommendations = [
        OpportunityRecommendation(
            ticker='REGN',
            thesis='Regtech providers set to benefit from mandatory AI compliance reporting mandates.',
            expected_return_pct=6.8,
            conviction=0.67,
            horizon_days=45,
            catalysts=['SEC modernization', 'State privacy rules'],
            risk_rating='medium',
        ),
        OpportunityRecommendation(
            ticker='AIQ',
            thesis='AI infrastructure ETF gains from public sector procurement reforms favoring automation vendors.',
            expected_return_pct=5.4,
            conviction=0.62,
            horizon_days=30,
            catalysts=['Federal AI procurement bill', 'Defense modernization budget'],
            risk_rating='medium',
        ),
        OpportunityRecommendation(
            ticker='CSPN',
            thesis='Cybersecurity firms positioned for upside amid pending state-level disclosure standards.',
            expected_return_pct=4.1,
            conviction=0.58,
            horizon_days=60,
            catalysts=['State privacy frameworks', 'Federal oversight expansion'],
            risk_rating='balanced',
        ),
        OpportunityRecommendation(
            ticker='GRID',
            thesis='Grid modernization vendors benefit from infrastructure resilience funding.',
            expected_return_pct=3.6,
            conviction=0.52,
            horizon_days=75,
            catalysts=['Infrastructure grants', 'Resilience task force'],
            risk_rating='low',
        ),
    ]

    filtered = [
        item
        for item in recommendations
        if _matches_filters(item, risk_ratings, min_conviction, max_horizon_days)
    ]
    opportunities = (filtered or recommendations)[:limit]
    return OpportunityPayload(
        generated_at=generated_at,
        opportunities=opportunities,
        applied_filters=_build_applied_filters(
            risk_ratings, min_conviction, max_horizon_days
        ),
    )


def _matches_filters(
    item: OpportunityRecommendation,
    risk_ratings: list[str] | None,
    min_conviction: float | None,
    max_horizon_days: int | None,
) -> bool:
    if risk_ratings and item.risk_rating.lower() not in risk_ratings:
        return False
    if min_conviction is not None and item.conviction < min_conviction:
        return False
    if max_horizon_days is not None and item.horizon_days > max_horizon_days:
        return False
    return True


def _build_applied_filters(
    risk_ratings: list[str] | None,
    min_conviction: float | None,
    max_horizon_days: int | None,
) -> dict[str, object] | None:
    filters = {}
    if risk_ratings:
        filters['risk_ratings'] = risk_ratings
    if min_conviction is not None:
        filters['min_conviction'] = min_conviction
    if max_horizon_days is not None:
        filters['max_horizon_days'] = max_horizon_days
    return filters or None
