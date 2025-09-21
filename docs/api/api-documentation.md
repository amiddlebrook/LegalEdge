# LegalEdge API Documentation

Welcome to the LegalEdge API documentation. This comprehensive guide provides everything you need to integrate with our AI-driven legislative intelligence platform.

## Overview

LegalEdge provides AI-powered legislative intelligence and investment insights through a RESTful API. Our platform helps investors, analysts, and businesses understand how legislation affects their investments and identify market opportunities.

### Base URL
```
https://api.legaledge.com/v1
```

### Authentication
All API requests require authentication using JWT tokens:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     https://api.legaledge.com/v1/legislation/
```

### Response Format
All responses are returned in JSON format with consistent structure:

```json
{
  "data": {
    // Response data
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req-123456",
    "version": "v1.0.0"
  }
}
```

## Authentication

### Register User
Create a new user account.

**Endpoint:** `POST /auth/register`

**Request:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "secure_password",
  "full_name": "Full Name"
}
```

**Response:**
```json
{
  "data": {
    "id": "user-123",
    "email": "user@example.com",
    "username": "username",
    "full_name": "Full Name",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Login
Authenticate user and receive JWT token.

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "username": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

### Refresh Token
Refresh access token using refresh token.

**Endpoint:** `POST /auth/refresh`

**Request:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Legislation

### List Legislation
Retrieve legislation with optional filtering.

**Endpoint:** `GET /legislation/`

**Query Parameters:**
- `limit` (int): Number of results to return (default: 20, max: 100)
- `offset` (int): Number of results to skip (default: 0)
- `jurisdiction` (string): Filter by jurisdiction (federal, california, texas, etc.)
- `status` (string): Filter by status (introduced, passed, failed, pending)
- `topics` (string): Comma-separated list of topics
- `since_date` (string): Only return legislation after this date (YYYY-MM-DD)

**Example:**
```bash
curl "https://api.legaledge.com/v1/legislation/?jurisdiction=federal&status=introduced&limit=10"
```

**Response:**
```json
{
  "data": [
    {
      "id": "bill-123",
      "title": "AI Regulation Act of 2024",
      "summary": "Comprehensive regulation of artificial intelligence...",
      "status": "introduced",
      "jurisdiction": "federal",
      "bill_number": "HB-1234",
      "introduced_date": "2024-01-15",
      "sponsors": ["Rep. John Doe", "Sen. Jane Smith"],
      "topics": ["artificial intelligence", "technology", "regulation"],
      "sentiment_score": 0.7,
      "enactment_probability": 0.85,
      "impact_score": 8.5,
      "full_text_url": "https://example.com/bill-text",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "meta": {
    "total_count": 150,
    "has_more": true
  }
}
```

### Get Legislation by ID
Retrieve detailed information about a specific piece of legislation.

**Endpoint:** `GET /legislation/{bill_id}`

**Example:**
```bash
curl "https://api.legaledge.com/v1/legislation/bill-123"
```

### Search Legislation
Full-text search across legislation titles and content.

**Endpoint:** `GET /legislation/search`

**Query Parameters:**
- `query` (string, required): Search query
- `jurisdiction` (string): Filter by jurisdiction
- `status` (string): Filter by status
- `topics` (string): Comma-separated list of topics
- `limit` (int): Number of results (default: 20)
- `offset` (int): Results offset (default: 0)

### Get Legislation by Topics
Retrieve legislation filtered by specific topics.

**Endpoint:** `GET /legislation/topics/{topics}`

**Path Parameters:**
- `topics` (string): Comma-separated list of topics

**Example:**
```bash
curl "https://api.legaledge.com/v1/legislation/topics/artificial%20intelligence,technology"
```

### Get Legislation by Jurisdiction
Retrieve legislation from a specific jurisdiction.

**Endpoint:** `GET /legislation/jurisdiction/{jurisdiction}`

**Example:**
```bash
curl "https://api.legaledge.com/v1/legislation/jurisdiction/federal"
```

## Portfolios

### Create Portfolio
Create a new investment portfolio.

**Endpoint:** `POST /portfolios/`

**Request:**
```json
{
  "name": "Tech Growth Portfolio",
  "description": "Portfolio focused on technology companies",
  "tickers": ["AAPL", "MSFT", "GOOGL", "NVDA"]
}
```

**Response:**
```json
{
  "data": {
    "id": "portfolio-456",
    "name": "Tech Growth Portfolio",
    "description": "Portfolio focused on technology companies",
    "tickers": ["AAPL", "MSFT", "GOOGL", "NVDA"],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### List Portfolios
Retrieve user's portfolios.

**Endpoint:** `GET /portfolios/`

### Get Portfolio
Retrieve specific portfolio details.

**Endpoint:** `GET /portfolios/{portfolio_id}`

### Update Portfolio
Update portfolio information.

**Endpoint:** `PUT /portfolios/{portfolio_id}`

**Request:**
```json
{
  "name": "Updated Portfolio Name",
  "description": "Updated description",
  "tickers": ["TSLA", "NVDA", "AMD"]
}
```

### Delete Portfolio
Delete a portfolio.

**Endpoint:** `DELETE /portfolios/{portfolio_id}`

### Get Portfolio Conflicts
Analyze conflicts between portfolio holdings and legislation.

**Endpoint:** `GET /portfolios/{portfolio_id}/conflicts/{bill_id}`

**Response:**
```json
{
  "data": {
    "conflict_score": 0.8,
    "risk_factors": ["regulatory_risk", "compliance_cost"],
    "affected_tickers": ["AAPL", "MSFT"],
    "recommendations": [
      "Consider reducing exposure to affected companies",
      "Monitor legislative progress closely"
    ]
  }
}
```

## Alerts

### Create Alert Configuration
Create a new alert configuration.

**Endpoint:** `POST /alerts/config`

**Request:**
```json
{
  "name": "AI Regulation Alerts",
  "description": "Alerts for AI-related legislation",
  "keywords": ["artificial intelligence", "machine learning", "AI regulation"],
  "jurisdictions": ["federal", "california"],
  "severity_threshold": "medium",
  "notification_channels": ["email", "webhook"]
}
```

### List Alert Configurations
Retrieve user's alert configurations.

**Endpoint:** `GET /alerts/config`

### Get Alert Feed
Retrieve user's alerts feed.

**Endpoint:** `GET /alerts/feed`

**Query Parameters:**
- `limit` (int): Number of alerts (default: 20)
- `offset` (int): Offset for pagination (default: 0)
- `category` (string): Filter by category (legislation, market, portfolio, system)
- `severity` (string): Filter by severity (low, medium, high, critical)
- `unread_only` (bool): Only return unread alerts

### Update Alert Configuration
Update alert configuration.

**Endpoint:** `PUT /alerts/config/{config_id}`

### Delete Alert Configuration
Delete alert configuration.

**Endpoint:** `DELETE /alerts/config/{config_id}`

### Mark Alert as Read
Mark an alert as read.

**Endpoint:** `PUT /alerts/{alert_id}/read`

## Dashboard

### Get Dashboard Overview
Retrieve comprehensive dashboard overview.

**Endpoint:** `GET /dashboard/overview`

**Response:**
```json
{
  "data": {
    "total_portfolios": 3,
    "active_alerts": 12,
    "pending_legislation": 45,
    "market_opportunities": 8,
    "portfolio_conflicts": 2,
    "recent_activity": [...]
  }
}
```

### Get Coverage Metrics
Retrieve platform coverage metrics.

**Endpoint:** `GET /dashboard/coverage`

### Get Market Opportunities
Retrieve market opportunity recommendations.

**Endpoint:** `GET /dashboard/opportunities`

**Query Parameters:**
- `limit` (int): Number of opportunities (default: 10)
- `min_confidence` (float): Minimum confidence score (default: 0.5)

### Get Forecasts
Retrieve market forecasts.

**Endpoint:** `GET /dashboard/forecasts`

**Query Parameters:**
- `tickers` (string): Comma-separated list of tickers
- `days_ahead` (int): Number of days to forecast (default: 30)

## Webhooks

### Register Webhook
Register a webhook endpoint for real-time notifications.

**Endpoint:** `POST /webhooks/`

**Request:**
```json
{
  "url": "https://your-app.com/webhooks/legaledge",
  "events": ["legislation.created", "alerts.created", "opportunities.found"],
  "secret": "your_webhook_secret"
}
```

### List Webhooks
Retrieve registered webhooks.

**Endpoint:** `GET /webhooks/`

### Delete Webhook
Delete a webhook.

**Endpoint:** `DELETE /webhooks/{webhook_id}`

### Test Webhook
Send a test payload to webhook endpoint.

**Endpoint:** `POST /webhooks/{webhook_id}/test`

## Rate Limits

API requests are rate limited to ensure fair usage:

- **Free Tier**: 100 requests per hour
- **Pro Tier**: 1,000 requests per hour
- **Enterprise Tier**: 10,000 requests per hour

Rate limit information is included in response headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 2024-01-15T11:00:00Z
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req-123456"
  }
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

## SDKs and Libraries

### Python SDK
```bash
pip install legaledge-sdk
```

```python
from legaledge import LegalEdgeClient

client = LegalEdgeClient(api_key="your_api_key")

# Search legislation
legislation = client.legislation.search("artificial intelligence")

# Get portfolio conflicts
conflicts = client.portfolios.get_conflicts("portfolio-123", "bill-456")
```

### JavaScript SDK
```bash
npm install legaledge-js
```

```javascript
const { LegalEdgeClient } = require('legaledge-js');

const client = new LegalEdgeClient({ apiKey: 'your_api_key' });

// Search legislation
const legislation = await client.legislation.search('artificial intelligence');

// Get portfolio conflicts
const conflicts = await client.portfolios.getConflicts('portfolio-123', 'bill-456');
```

## Support

For API support and questions:
- **Email**: api-support@legaledge.com
- **Documentation**: https://docs.legaledge.com
- **Status Page**: https://status.legaledge.com
- **Community**: https://community.legaledge.com

## Changelog

### Version 1.0.0 (Current)
- Initial API release
- Core endpoints: legislation, portfolios, alerts, dashboard
- Authentication and authorization
- Rate limiting
- Webhook support

### Upcoming Features
- Real-time streaming API
- Advanced analytics endpoints
- Bulk operations
- Enhanced filtering options
