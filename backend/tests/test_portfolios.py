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


def test_portfolio_summary_endpoint():
    client = TestClient(create_application())
    response = client.get('/api/v1/portfolios/summary', params={'lookback_days': 60, 'top_n': 3})
    assert response.status_code == 200
    payload = response.json()
    assert payload['total_trades_30d'] >= 1
    assert payload['top_tickers']
