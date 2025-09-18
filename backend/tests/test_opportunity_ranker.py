import pytest

from app.ml.opportunity_ranker import rank_opportunities
from app.schemas.opportunity import OpportunityRecommendation


@pytest.mark.anyio
async def test_rank_opportunities_returns_sorted_results():
    base = [
        OpportunityRecommendation(
            ticker='REGN',
            thesis='Regtech play',
            expected_return_pct=6.5,
            conviction=0.7,
            horizon_days=40,
            catalysts=['Regulation shift'],
            risk_rating='medium',
        ),
        OpportunityRecommendation(
            ticker='GRID',
            thesis='Grid modernization tailwind',
            expected_return_pct=3.8,
            conviction=0.55,
            horizon_days=60,
            catalysts=['Infrastructure grants'],
            risk_rating='low',
        ),
    ]

    ranked, metadata = await rank_opportunities(base, session=None)

    assert metadata['ranker_version']
    assert ranked
    assert ranked[0].composite_score is not None
    if len(ranked) > 1 and ranked[1].composite_score is not None:
        assert ranked[0].composite_score >= ranked[1].composite_score
    assert ranked[0].drivers
    assert ranked[0].explanation
