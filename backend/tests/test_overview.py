from fastapi.testclient import TestClient

from app.main import create_application


def test_overview_payload_shape():
    client = TestClient(create_application())
    response = client.get('/api/v1/overview')
    assert response.status_code == 200
    payload = response.json()

    assert payload['hero']['kicker']
    assert isinstance(payload['data_sources'], list)
    assert payload['features'] and payload['metrics'] and payload['workflow']