"""Portfolio tracker endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import maybe_get_session
from app.schemas.portfolio import ConflictInsight, PortfolioSignal, PortfolioSnapshot, TradeTimelinePoint, MemberExposure, TradeActivity
from app.services.portfolio import aggregate_signals, detect_conflicts, get_portfolio_snapshot, get_trade_activity_timeline, get_member_exposures, get_member_trade_history


router = APIRouter(prefix="/portfolios", tags=["Portfolios"])


@router.get(
    "/signals",
    response_model=list[PortfolioSignal],
    summary="Signals derived from congressional trades",
)
async def portfolio_signals(
    limit: int = Query(default=5, ge=1, le=25),
    session: AsyncSession | None = Depends(maybe_get_session),
) -> list[PortfolioSignal]:
    """Expose AI prioritized portfolio signals."""

    return await aggregate_signals(limit=limit, session=session)


@router.get(
    "/summary",
    response_model=PortfolioSnapshot,
    summary="Portfolio activity snapshot",
)
async def portfolio_summary(
    session: AsyncSession | None = Depends(maybe_get_session),
    lookback_days: int = Query(default=30, ge=1, le=120),
    top_n: int = Query(default=5, ge=1, le=20),
) -> PortfolioSnapshot:
    """Expose aggregated congressional trading metrics."""

    return await get_portfolio_snapshot(session=session, lookback_days=lookback_days, top_n=top_n)


@router.get(
    '/timeline',
    response_model=list[TradeTimelinePoint],
    summary='Daily trade activity timeline',
)
async def portfolio_timeline(
    lookback_days: int = Query(default=30, ge=1, le=120),
    tickers: list[str] | None = Query(default=None),
    session: AsyncSession | None = Depends(maybe_get_session),
) -> list[TradeTimelinePoint]:
    """Expose daily trading volume detail for congressional disclosures."""

    return await get_trade_activity_timeline(
        session=session, lookback_days=lookback_days, tickers=tickers
    )


@router.get(
    '/members/exposures',
    response_model=list[MemberExposure],
    summary='Member trading exposure',
)
async def portfolio_member_exposures(
    lookback_days: int = Query(default=30, ge=1, le=120),
    limit: int = Query(default=10, ge=1, le=50),
    session: AsyncSession | None = Depends(maybe_get_session),
) -> list[MemberExposure]:
    """Expose trading activity rollups per congressional member."""

    return await get_member_exposures(session=session, lookback_days=lookback_days, limit=limit)


@router.get(
    '/members/{member}/trades',
    response_model=list[TradeActivity],
    summary='Member trade history',
)
async def portfolio_member_history(
    member: str,
    lookback_days: int = Query(default=180, ge=1, le=365),
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession | None = Depends(maybe_get_session),
) -> list[TradeActivity]:
    """Expose detailed trade history for a specific member."""

    return await get_member_trade_history(
        member=member, session=session, lookback_days=lookback_days, limit=limit
    )
@router.get(
    "/conflicts",
    response_model=list[ConflictInsight],
    summary="Potential conflicts between trades and policy",
)
async def portfolio_conflicts(
    limit: int = Query(default=5, ge=1, le=25),
    session: AsyncSession | None = Depends(maybe_get_session),
) -> list[ConflictInsight]:
    """Expose possible conflicts between congressional trading and policy momentum."""

    return await detect_conflicts(limit=limit, session=session)



