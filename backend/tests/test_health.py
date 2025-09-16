from fastapi.testclient import TestClient

from app.main import create_application


def test_health_status():
    client = TestClient(create_application())
    response = client.get('/api/v1/health/status')
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'ok'