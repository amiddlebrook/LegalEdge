from fastapi.testclient import TestClient

from app.main import create_application


client = TestClient(create_application())


def test_alert_feed():
    response = client.get('/api/v1/alerts')
    assert response.status_code == 200
    payload = response.json()

    assert len(payload['alerts']) > 0
    assert payload['alerts'][0]['severity']


def test_alert_feed_filters_by_severity_and_category():
    response = client.get('/api/v1/alerts', params={'min_severity': 'high', 'categories': 'Legislation'})
    assert response.status_code == 200
    payload = response.json()

    assert payload['alerts']
    for alert in payload['alerts']:
        assert alert['severity'].lower() in {'high', 'critical'}
        assert alert['category'].lower() == 'legislation'

    assert payload['applied_filters']['min_severity'] == 'high'
    assert 'Legislation' in payload['applied_filters']['categories']

