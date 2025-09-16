"""Market correlation and forecasting stubs."""
from datetime import date

from app.schemas.forecast import ForecastBreakdown, ForecastEnvelope


async def build_sector_forecast(sector: str, horizon_days: int = 30) -> ForecastEnvelope:
    """Return a deterministic payload until the ML pipeline is connected."""

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