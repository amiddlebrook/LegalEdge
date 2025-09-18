"""Opportunity recommendation services."""
from datetime import datetime, timezone
from typing import Iterable

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.opportunity_ranker import rank_opportunities
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
    """Return opportunity recommendations enriched with ranking metadata."""

    logger.debug('Generating %s market opportunities', limit)
    normalized_risks = _normalize_risk_filters(risk_ratings)

    base_recommendations: list[OpportunityRecommendation] = []
    generated_at: datetime | None = None

    if session is not None:
        try:
            records = await list_opportunities(
                session,
                limit=limit,
                risk_ratings=normalized_risks,
                min_conviction=min_conviction,
                max_horizon_days=max_horizon_days,
            )
        except Exception as exc:  # pragma: no cover - defensive log
            logger.warning('Failed to fetch opportunities from DB: %s', exc)
        else:
            if records:
                logger.debug('Serving %s opportunity records from database', len(records))
                generated_at = records[0].updated_at or records[0].created_at or datetime.now(timezone.utc)
                base_recommendations = [
                    OpportunityRecommendation(
                        ticker=item.ticker,
                        thesis=item.thesis,
                        expected_return_pct=item.expected_return_pct,
                        conviction=item.conviction,
                        horizon_days=item.horizon_days,
                        catalysts=list(item.catalysts or []),
                        risk_rating=item.risk_rating,
                    )
                    for item in records
                ]

    if not base_recommendations:
        fallback = _fallback_payload(
            limit=limit,
            risk_ratings=normalized_risks,
            min_conviction=min_conviction,
            max_horizon_days=max_horizon_days,
        )
        base_recommendations = fallback.opportunities
        generated_at = fallback.generated_at
        logger.debug('Falling back to stubbed opportunity recommendations')

    horizon_hint = max_horizon_days or max((item.horizon_days for item in base_recommendations), default=45)
    ranked, metadata = await rank_opportunities(
        base_recommendations,
        session=session,
        horizon_days=horizon_hint,
    )

    ordered = ranked[:limit]
    applied_filters = _build_applied_filters(risk_ratings, min_conviction, max_horizon_days)

    return OpportunityPayload(
        generated_at=generated_at or datetime.now(timezone.utc),
        opportunities=ordered,
        applied_filters=applied_filters,
        ranker_version=metadata.get('ranker_version'),
        scoring_notes=metadata.get('scoring_notes'),
        top_drivers=metadata.get('top_drivers'),
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
            composite_score=0.74,
            policy_alignment=0.68,
            conflict_score=0.22,
            drivers=['SEC modernization', 'State privacy rules'],
            explanation='Regtech signals align with compliance modernization momentum across federal and state venues.',
        ),
        OpportunityRecommendation(
            ticker='AIQ',
            thesis='AI infrastructure ETF gains from public sector procurement reforms favoring automation vendors.',
            expected_return_pct=5.4,
            conviction=0.62,
            horizon_days=30,
            catalysts=['Federal AI procurement bill', 'Defense modernization budget'],
            risk_rating='medium',
            composite_score=0.71,
            policy_alignment=0.66,
            conflict_score=0.18,
            drivers=['Federal AI procurement bill', 'Defense modernization budget'],
            explanation='Procurement legislation momentum supports AIQ positioning with minimal conflict drag observed.',
        ),
        OpportunityRecommendation(
            ticker='CSPN',
            thesis='Cybersecurity firms positioned for upside amid pending state-level disclosure standards.',
            expected_return_pct=4.1,
            conviction=0.58,
            horizon_days=60,
            catalysts=['State privacy frameworks', 'Federal oversight expansion'],
            risk_rating='balanced',
            composite_score=0.62,
            policy_alignment=0.58,
            conflict_score=0.31,
            drivers=['State privacy frameworks', 'Federal oversight expansion'],
            explanation='Privacy oversight proposals bolster CSPN demand despite moderate conflict friction to monitor.',
        ),
        OpportunityRecommendation(
            ticker='GRID',
            thesis='Grid modernization vendors benefit from infrastructure resilience funding.',
            expected_return_pct=3.6,
            conviction=0.52,
            horizon_days=75,
            catalysts=['Infrastructure grants', 'Resilience task force'],
            risk_rating='low',
            composite_score=0.59,
            policy_alignment=0.54,
            conflict_score=0.16,
            drivers=['Infrastructure grants', 'Resilience task force'],
            explanation='Infrastructure funding continues to support GRID with limited conflict risk observed in disclosures.',
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
