from fastapi.testclient import TestClient

from app.main import create_application


def test_alert_feed():
    client = TestClient(create_application())
    response = client.get('/api/v1/alerts')
    assert response.status_code == 200
    payload = response.json()

    assert len(payload['alerts']) > 0
    assert payload['alerts'][0]['severity']