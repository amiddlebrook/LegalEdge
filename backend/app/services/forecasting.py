"""Market correlation and forecasting services."""
from datetime import date

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.forecaster import Forecaster, ForecastBundle, get_forecaster
from app.repositories.forecast import list_sector_forecast
from app.schemas.forecast import ForecastBreakdown, ForecastEnvelope


async def build_sector_forecast(
    sector: str,
    horizon_days: int = 30,
    *,
    session: AsyncSession | None = None,
) -> ForecastEnvelope:
    """Return forecast data, preferring database-backed signals when available."""

    forecaster = get_forecaster()
    db_breakdown: list[ForecastBreakdown] | None = None
    generated_on: date | None = None
    tickers: list[str] = []

    if session is not None:
        try:
            signals = await list_sector_forecast(session, sector=sector, limit=10)
        except Exception as exc:  # pragma: no cover - defensive log
            logger.warning("Failed to fetch forecasts from DB: %s", exc)
        else:
            if signals:
                logger.debug("Serving %s forecast signals from database", len(signals))
                tickers = [signal.ticker for signal in signals]
                db_breakdown = [
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

    bundle = await _ensure_bundle(
        forecaster=forecaster,
        sector=sector,
        horizon_days=horizon_days,
        tickers=tickers or None,
    )

    if db_breakdown is not None and generated_on is not None:
        return ForecastEnvelope(
            sector=sector,
            horizon_days=horizon_days,
            generated_on=generated_on,
            signals=db_breakdown,
            estimated_accuracy=bundle.estimated_accuracy,
            methodology_summary=bundle.methodology_summary,
            drivers=bundle.drivers or None,
        )

    signals_payload = [
        ForecastBreakdown(
            ticker=signal.ticker,
            thesis=signal.thesis,
            expected_return_pct=signal.expected_return_pct,
            confidence=signal.confidence,
            catalysts=signal.catalysts,
        )
        for signal in bundle.signals
    ]

    return ForecastEnvelope(
        sector=sector,
        horizon_days=horizon_days,
        generated_on=bundle.generated_on,
        signals=signals_payload,
        estimated_accuracy=bundle.estimated_accuracy,
        methodology_summary=bundle.methodology_summary,
        drivers=bundle.drivers or None,
    )


async def _ensure_bundle(
    *,
    forecaster: Forecaster,
    sector: str,
    horizon_days: int,
    tickers: list[str] | None,
) -> ForecastBundle:
    try:
        return await forecaster.forecast_sector(
            sector=sector,
            horizon_days=horizon_days,
            tickers=tickers,
        )
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.warning("Falling back to default forecasting bundle for %s: %s", sector, exc)
        return ForecastBundle(
            sector=sector,
            horizon_days=horizon_days,
            generated_on=date.today(),
            signals=[],
            estimated_accuracy=0.72,
            methodology_summary='Fallback forecasting bundle due to runtime error.',
        )
