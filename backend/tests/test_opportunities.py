from fastapi.testclient import TestClient

from app.main import create_application


def test_opportunities_endpoint():
    client = TestClient(create_application())
    response = client.get('/api/v1/opportunities?limit=2')
    assert response.status_code == 200
    payload = response.json()

    assert len(payload['opportunities']) == 2
    assert payload['generated_at']