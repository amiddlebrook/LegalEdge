"""Portfolio tracker endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import maybe_get_session
from app.schemas.portfolio import PortfolioSignal
from app.services.portfolio import aggregate_signals


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