import pytest

from app.ml.forecaster import Forecaster


@pytest.fixture
def forecaster():
    return Forecaster()


@pytest.mark.anyio
async def test_forecaster_generates_signals(forecaster):
    bundle = await forecaster.forecast_sector(sector='Technology', horizon_days=45)

    assert bundle.sector == 'Technology'
    assert bundle.signals
    assert bundle.estimated_accuracy >= 0.7
    assert bundle.methodology_summary

    first = bundle.signals[0]
    assert -6.0 <= first.expected_return_pct <= 15.0
    assert 0.45 <= first.confidence <= 0.92
    assert first.catalysts


@pytest.mark.anyio
async def test_forecaster_retrain_adjusts_accuracy(forecaster, monkeypatch):
    base_accuracy = forecaster._baseline_accuracy

    async def fake_retrain():
        return None

    monkeypatch.setattr(forecaster._pipeline, 'retrain', fake_retrain)
    forecaster._last_trained_at = forecaster._last_trained_at.replace(year=forecaster._last_trained_at.year - 1)

    await forecaster.retrain()
    assert forecaster._baseline_accuracy >= base_accuracy
