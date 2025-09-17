from fastapi.testclient import TestClient

from app.main import create_application


def test_portfolio_conflicts_endpoint():
    client = TestClient(create_application())
    response = client.get('/api/v1/portfolios/conflicts')
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert 0 <= payload[0]['risk_score'] <= 1
    assert payload[0]['ticker']
