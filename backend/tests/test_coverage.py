from fastapi.testclient import TestClient

from app.main import create_application


def test_coverage_summary_endpoint():
    client = TestClient(create_application())
    response = client.get('/api/v1/coverage')
    assert response.status_code == 200

    payload = response.json()
    assert payload['jurisdictions']
    assert payload['processing_health']['processing_sla_minutes'] >= payload['processing_health']['ingestion_latency_minutes']
