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



def test_alert_subscription_workflow():
    payload = {
        'subscriber_id': 'qa-alerts@legaledge.ai',
        'label': 'QA coverage checks',
        'categories': ['Legislation'],
        'entities': ['HR-1001'],
        'severities': ['high'],
        'min_severity': 'high',
        'channels': [
            {'type': 'email', 'target': 'qa-alerts@legaledge.ai'},
            {'type': 'webhook', 'target': 'https://hooks.qa.legaledge.ai/alerts'},
        ],
    }
    response = client.post('/api/v1/alerts/subscriptions', json=payload)
    assert response.status_code == 201
    created = response.json()
    subscription_id = created['id']

    listing = client.get('/api/v1/alerts/subscriptions', params={'subscriber_id': payload['subscriber_id']})
    assert listing.status_code == 200
    items = listing.json()
    assert any(item['id'] == subscription_id for item in items)

    update = client.put(
        f'/api/v1/alerts/subscriptions/{subscription_id}',
        json={'entities': ['HR-1001', 'AIT'], 'min_severity': 'critical'},
    )
    assert update.status_code == 200
    assert update.json()['min_severity'] == 'critical'

    preview = client.get('/api/v1/alerts/dispatch/alert-hr1001/preview')
    assert preview.status_code == 200
    preview_body = preview.json()
    assert preview_body['total_channels'] >= 1

    dispatch = client.post('/api/v1/alerts/dispatch/alert-hr1001')
    assert dispatch.status_code == 200
    assert dispatch.json()['total_channels'] == preview_body['total_channels']

    delete = client.delete(f'/api/v1/alerts/subscriptions/{subscription_id}')
    assert delete.status_code == 204

    missing = client.get(f'/api/v1/alerts/subscriptions/{subscription_id}')
    assert missing.status_code == 404
