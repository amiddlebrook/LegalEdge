from fastapi.testclient import TestClient

from app.main import create_application


def test_opportunities_endpoint_returns_payload():
    client = TestClient(create_application())
    response = client.get('/api/v1/opportunities?limit=2')

    assert response.status_code == 200
    payload = response.json()
    assert len(payload['opportunities']) == 2
    assert payload['generated_at']
    assert payload['applied_filters'] is None


def test_opportunities_filters_reflected_in_response():
    client = TestClient(create_application())
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

    assert payload['applied_filters'] == {
        'risk_ratings': ['balanced', 'low'],
        'min_conviction': 0.55,
        'max_horizon_days': 60,
    }
    assert payload['opportunities'], 'expected at least one filtered opportunity'
    for item in payload['opportunities']:
        assert item['risk_rating'] in {'balanced', 'low'}
        assert item['conviction'] >= 0.55
        assert item['horizon_days'] <= 60
