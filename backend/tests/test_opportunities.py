from fastapi.testclient import TestClient

from app.main import create_application


def _client() -> TestClient:
    return TestClient(create_application())


def test_opportunities_endpoint_returns_payload():
    client = _client()
    response = client.get('/api/v1/opportunities?limit=2')

    assert response.status_code == 200
    payload = response.json()

    assert len(payload['opportunities']) == 2
    assert payload['generated_at']
    assert payload['applied_filters'] is None
    assert payload['ranker_version']
    assert payload['scoring_notes']

    first = payload['opportunities'][0]
    assert 'composite_score' in first
    assert 'policy_alignment' in first
    if len(payload['opportunities']) > 1:
        assert first['composite_score'] >= payload['opportunities'][1]['composite_score']


def test_opportunities_filters_reflected_in_response():
    client = _client()
    response = client.get(
        '/api/v1/opportunities',
        params={
            'risk_ratings': ['balanced', 'low'],
            'min_conviction': 0.55,
            'max_horizon_days': 60,
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload['ranker_version']
    assert payload['applied_filters'] == {
        'risk_ratings': ['balanced', 'low'],
        'min_conviction': 0.55,
        'max_horizon_days': 60,
    }
    assert payload['opportunities'], 'expected at least one filtered opportunity'
    for item in payload['opportunities']:
        assert 'composite_score' in item
        assert 'policy_alignment' in item
        assert item['risk_rating'] in {'balanced', 'low'}
        assert item['conviction'] >= 0.55
        assert item['horizon_days'] <= 60
