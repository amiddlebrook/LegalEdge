from fastapi.testclient import TestClient

from app.main import create_application


def test_dashboard_snapshot():
    client = TestClient(create_application())
    response = client.get('/api/v1/dashboard/snapshot')
    assert response.status_code == 200
    payload = response.json()

    assert len(payload['upcoming_legislation']) > 0
    assert payload['sector_forecast']['sector']
    assert len(payload['portfolio_signals']) > 0