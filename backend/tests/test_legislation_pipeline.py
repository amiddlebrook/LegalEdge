import pytest

from app.ml.legislation_pipeline import LegislationNlpPipeline


@pytest.fixture
def pipeline():
    return LegislationNlpPipeline(enable_transformers=False)


@pytest.mark.anyio
async def test_pipeline_analysis_positive_signal(pipeline):
    synopsis = (
        "The bill accelerates cloud modernization grants and establishes incentives "
        "for cybersecurity investments supporting AI infrastructure with bipartisan backing."
    )
    result = await pipeline.analyze(
        synopsis,
        bill_id='HR-2025',
        target_tickers=['AIT', 'GRID'],
        full_text=None,
        risk_appetite='balanced',
    )

    assert -1.0 <= result.sentiment <= 1.0
    assert result.sentiment > 0
    assert result.enactment_probability >= 0.1
    assert set(result.ticker_impacts.keys()) == {'AIT', 'GRID'}
    assert any(value > 0 for value in result.ticker_impacts.values())
    assert result.confidence >= 0.2
    assert result.drivers
    assert result.model_version


@pytest.mark.anyio
async def test_pipeline_analysis_negative_signal(pipeline):
    synopsis = (
        "Legislation imposes strict penalties, moratorium on federal procurement, and new enforcement actions "
        "creating compliance burdens and opposition from key committees."
    )
    result = await pipeline.analyze(
        synopsis,
        bill_id='S-4040',
        target_tickers=['REGN'],
        full_text=None,
        risk_appetite='conservative',
    )

    assert result.sentiment < 0
    assert result.ticker_impacts['REGN'] <= 0
    assert result.enactment_probability <= 0.8
    assert 'Risk factors cited' in ' '.join(result.drivers)


@pytest.mark.anyio
async def test_pipeline_retrain_updates_version(pipeline, monkeypatch):
    monkeypatch.setattr(pipeline, '_stamp_version', lambda: 'v1')
    await pipeline.retrain()
    assert pipeline._model_version == 'v1'

    monkeypatch.setattr(pipeline, '_stamp_version', lambda: 'v2')
    await pipeline.retrain()
    assert pipeline._model_version == 'v2'

