"""Opportunity recommendation services."""
from datetime import datetime, timezone

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.insights import list_opportunities
from app.schemas.opportunity import OpportunityPayload, OpportunityRecommendation


async def get_market_opportunities(
    limit: int = 5,
    *,
    session: AsyncSession | None = None,
) -> OpportunityPayload:
    logger.debug('Generating %s market opportunities', limit)
    """Return opportunity recommendations seeded in the database when available."""

    if session is not None:
        try:
            opportunities = await list_opportunities(session, limit=limit)
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
                )

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
    ]

    return OpportunityPayload(generated_at=generated_at, opportunities=recommendations[:limit])