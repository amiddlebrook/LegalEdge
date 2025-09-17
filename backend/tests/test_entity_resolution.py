from fastapi.testclient import TestClient

from app.main import create_application


client = TestClient(create_application())


def test_entity_resolution_summary_route():
    response = client.get('/api/v1/entity-resolution/summary')
    assert response.status_code == 200
    payload = response.json()

    assert 'metrics' in payload
    assert payload['bill_links']
    assert 0 <= payload['metrics']['coverage_ratio'] <= 1
    assert payload['top_entities']
