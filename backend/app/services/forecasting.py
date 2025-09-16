"""Market correlation and forecasting services."""
from datetime import date

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.forecast import list_sector_forecast
from app.schemas.forecast import ForecastBreakdown, ForecastEnvelope


async def build_sector_forecast(
    sector: str,
    horizon_days: int = 30,
    *,
    session: AsyncSession | None = None,
) -> ForecastEnvelope:
    """Return forecast data, preferring database-backed signals when available."""

    if session is not None:
        try:
            signals = await list_sector_forecast(session, sector=sector, limit=10)
        except Exception as exc:  # pragma: no cover - defensive log
            logger.warning("Failed to fetch forecasts from DB: %s", exc)
        else:
            if signals:
                logger.debug("Serving %s forecast signals from database", len(signals))
                breakdown = [
                    ForecastBreakdown(
                        ticker=signal.ticker,
                        thesis=signal.thesis,
                        expected_return_pct=signal.expected_return_pct,
                        confidence=signal.confidence,
                        catalysts=list(signal.catalysts or []),
                    )
                    for signal in signals
                ]
                generated_on = signals[0].generated_on
                return ForecastEnvelope(
                    sector=sector,
                    horizon_days=horizon_days,
                    generated_on=generated_on,
                    signals=breakdown,
                )

    logger.debug("Falling back to stubbed forecast data for sector %s", sector)
    breakdown = [
        ForecastBreakdown(
            ticker="AIQ",
            thesis="AI infrastructure demand rises as compliance burdens climb.",
            expected_return_pct=4.2,
            confidence=0.58,
            catalysts=["Federal disclosure mandates", "State AI audits"],
        ),
        ForecastBreakdown(
            ticker="REGN",
            thesis="Regtech vendors benefit from mandated policy reporting.",
            expected_return_pct=6.8,
            confidence=0.67,
            catalysts=["SEC modernization", "State privacy rules"],
        ),
    ]

    return ForecastEnvelope(
        sector=sector,
        horizon_days=horizon_days,
        generated_on=date.today(),
        signals=breakdown,
    )