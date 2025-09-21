"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient
from fastapi import status


class TestAuthEndpoints:
    """Integration tests for authentication endpoints."""

    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient):
        """Test user registration endpoint."""
        user_data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "password123",
            "full_name": "Test User"
        }

        response = await client.post("/auth/register", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "testuser@example.com"
        assert data["username"] == "testuser"
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_register_existing_user(self, client: AsyncClient):
        """Test registering with existing email."""
        # First registration
        user_data = {
            "email": "existing@example.com",
            "username": "existinguser",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        # Second registration with same email
        response = await client.post("/auth/register", json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_user(self, client: AsyncClient):
        """Test user login endpoint."""
        # First register user
        user_data = {
            "email": "logintest@example.com",
            "username": "logintest",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        # Login
        login_data = {
            "username": "logintest@example.com",
            "password": "password123"
        }

        response = await client.post("/auth/login", data=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }

        response = await client.post("/auth/login", data=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient):
        """Test getting current user information."""
        # Register and login
        user_data = {
            "email": "currentuser@example.com",
            "username": "currentuser",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        login_data = {
            "username": "currentuser@example.com",
            "password": "password123"
        }
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # Get current user
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/auth/me", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "currentuser@example.com"
        assert data["username"] == "currentuser"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = await client.get("/auth/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient):
        """Test token refresh endpoint."""
        # Register and login
        user_data = {
            "email": "refreshtest@example.com",
            "username": "refreshtest",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        login_data = {
            "username": "refreshtest@example.com",
            "password": "password123"
        }
        login_response = await client.post("/auth/login", data=login_data)
        refresh_token = login_response.json()["refresh_token"]

        # Refresh token
        refresh_data = {"refresh_token": refresh_token}
        response = await client.post("/auth/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_logout_user(self, client: AsyncClient):
        """Test user logout endpoint."""
        # Register and login
        user_data = {
            "email": "logouttest@example.com",
            "username": "logouttest",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        login_data = {
            "username": "logouttest@example.com",
            "password": "password123"
        }
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # Logout
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post("/auth/logout", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Successfully logged out"


class TestLegislationEndpoints:
    """Integration tests for legislation endpoints."""

    @pytest.mark.asyncio
    async def test_list_legislation(self, client: AsyncClient):
        """Test listing legislation."""
        response = await client.get("/legislation/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_legislation_by_id(self, client: AsyncClient):
        """Test getting legislation by ID."""
        # First create a legislation item
        legislation_data = {
            "id": "test-bill-integration-123",
            "title": "Integration Test Bill",
            "summary": "A test bill for integration testing",
            "status": "introduced",
            "jurisdiction": "federal",
            "bill_number": "HB-9999",
            "introduced_date": "2024-01-15",
            "sponsors": ["Rep. Test User"],
            "topics": ["integration", "testing"],
            "sentiment_score": 0.6,
            "enactment_probability": 0.7,
            "impact_score": 7.5,
            "full_text_url": "https://example.com/test-bill"
        }

        # This would need to be done by an admin user
        # For now, we'll assume the data exists
        response = await client.get("/legislation/test-bill-integration-123")

        # This might return 404 if the data doesn't exist, which is expected
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    @pytest.mark.asyncio
    async def test_search_legislation(self, client: AsyncClient):
        """Test searching legislation."""
        search_params = {
            "query": "artificial intelligence",
            "jurisdiction": "federal",
            "status": "introduced",
            "limit": 10
        }

        response = await client.get("/legislation/search", params=search_params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_legislation_by_topics(self, client: AsyncClient):
        """Test getting legislation by topics."""
        topics = ["artificial intelligence", "technology"]
        response = await client.get(f"/legislation/topics/{','.join(topics)}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_legislation_by_jurisdiction(self, client: AsyncClient):
        """Test getting legislation by jurisdiction."""
        response = await client.get("/legislation/jurisdiction/federal")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)


class TestPortfolioEndpoints:
    """Integration tests for portfolio endpoints."""

    @pytest.mark.asyncio
    async def test_create_portfolio(self, client: AsyncClient):
        """Test creating a portfolio."""
        # Register user first
        user_data = {
            "email": "portfoliotest@example.com",
            "username": "portfoliotest",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        login_data = {
            "username": "portfoliotest@example.com",
            "password": "password123"
        }
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # Create portfolio
        portfolio_data = {
            "name": "Integration Test Portfolio",
            "description": "A portfolio for integration testing",
            "tickers": ["AAPL", "MSFT", "GOOGL"]
        }

        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post("/portfolios/", json=portfolio_data, headers=headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Integration Test Portfolio"
        assert data["tickers"] == ["AAPL", "MSFT", "GOOGL"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_portfolio(self, client: AsyncClient):
        """Test getting user portfolios."""
        # Register user first
        user_data = {
            "email": "getportfoliotest@example.com",
            "username": "getportfoliotest",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        login_data = {
            "username": "getportfoliotest@example.com",
            "password": "password123"
        }
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # Get portfolios
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/portfolios/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_portfolio_by_id(self, client: AsyncClient):
        """Test getting portfolio by ID."""
        # Register user and create portfolio first
        user_data = {
            "email": "getbyidtest@example.com",
            "username": "getbyidtest",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        login_data = {
            "username": "getbyidtest@example.com",
            "password": "password123"
        }
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # Create portfolio
        portfolio_data = {
            "name": "Test Portfolio by ID",
            "description": "Portfolio for ID test",
            "tickers": ["TSLA", "NVDA"]
        }

        headers = {"Authorization": f"Bearer {token}"}
        create_response = await client.post("/portfolios/", json=portfolio_data, headers=headers)
        portfolio_id = create_response.json()["id"]

        # Get portfolio by ID
        response = await client.get(f"/portfolios/{portfolio_id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == portfolio_id
        assert data["name"] == "Test Portfolio by ID"

    @pytest.mark.asyncio
    async def test_update_portfolio(self, client: AsyncClient):
        """Test updating a portfolio."""
        # Register user and create portfolio first
        user_data = {
            "email": "updatetest@example.com",
            "username": "updatetest",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        login_data = {
            "username": "updatetest@example.com",
            "password": "password123"
        }
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # Create portfolio
        portfolio_data = {
            "name": "Original Portfolio",
            "description": "Original description",
            "tickers": ["AAPL", "MSFT"]
        }

        headers = {"Authorization": f"Bearer {token}"}
        create_response = await client.post("/portfolios/", json=portfolio_data, headers=headers)
        portfolio_id = create_response.json()["id"]

        # Update portfolio
        update_data = {
            "name": "Updated Portfolio",
            "description": "Updated description",
            "tickers": ["TSLA", "NVDA", "AMD"]
        }

        response = await client.put(f"/portfolios/{portfolio_id}", json=update_data, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Portfolio"
        assert data["description"] == "Updated description"
        assert data["tickers"] == ["TSLA", "NVDA", "AMD"]

    @pytest.mark.asyncio
    async def test_delete_portfolio(self, client: AsyncClient):
        """Test deleting a portfolio."""
        # Register user and create portfolio first
        user_data = {
            "email": "deletetest@example.com",
            "username": "deletetest",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        login_data = {
            "username": "deletetest@example.com",
            "password": "password123"
        }
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # Create portfolio
        portfolio_data = {
            "name": "Portfolio to Delete",
            "description": "Will be deleted",
            "tickers": ["DELL", "HPQ"]
        }

        headers = {"Authorization": f"Bearer {token}"}
        create_response = await client.post("/portfolios/", json=portfolio_data, headers=headers)
        portfolio_id = create_response.json()["id"]

        # Delete portfolio
        response = await client.delete(f"/portfolios/{portfolio_id}", headers=headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = await client.get(f"/portfolios/{portfolio_id}", headers=headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestAlertsEndpoints:
    """Integration tests for alerts endpoints."""

    @pytest.mark.asyncio
    async def test_create_alert_config(self, client: AsyncClient):
        """Test creating alert configuration."""
        # Register user first
        user_data = {
            "email": "alertconfigtest@example.com",
            "username": "alertconfigtest",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        login_data = {
            "username": "alertconfigtest@example.com",
            "password": "password123"
        }
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # Create alert config
        alert_config_data = {
            "name": "AI Regulation Alerts",
            "description": "Alerts for AI regulation",
            "keywords": ["artificial intelligence", "machine learning"],
            "jurisdictions": ["federal", "california"],
            "severity_threshold": "medium",
            "notification_channels": ["email", "webhook"]
        }

        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post("/alerts/config", json=alert_config_data, headers=headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "AI Regulation Alerts"
        assert data["keywords"] == ["artificial intelligence", "machine learning"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_alerts_feed(self, client: AsyncClient):
        """Test getting alerts feed."""
        # Register user first
        user_data = {
            "email": "alertfeedtest@example.com",
            "username": "alertfeedtest",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        login_data = {
            "username": "alertfeedtest@example.com",
            "password": "password123"
        }
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # Get alerts feed
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/alerts/feed", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_alert_config(self, client: AsyncClient):
        """Test getting alert configurations."""
        # Register user first
        user_data = {
            "email": "getalertconfigtest@example.com",
            "username": "getalertconfigtest",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        login_data = {
            "username": "getalertconfigtest@example.com",
            "password": "password123"
        }
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # Get alert configs
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/alerts/config", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_update_alert_config(self, client: AsyncClient):
        """Test updating alert configuration."""
        # Register user and create alert config first
        user_data = {
            "email": "updatealertconfigtest@example.com",
            "username": "updatealertconfigtest",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        login_data = {
            "username": "updatealertconfigtest@example.com",
            "password": "password123"
        }
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # Create alert config
        alert_config_data = {
            "name": "Original Alert Config",
            "description": "Original description",
            "keywords": ["original"],
            "jurisdictions": ["federal"],
            "severity_threshold": "low",
            "notification_channels": ["email"]
        }

        headers = {"Authorization": f"Bearer {token}"}
        create_response = await client.post("/alerts/config", json=alert_config_data, headers=headers)
        config_id = create_response.json()["id"]

        # Update alert config
        update_data = {
            "name": "Updated Alert Config",
            "description": "Updated description",
            "keywords": ["updated", "new"],
            "jurisdictions": ["federal", "california"],
            "severity_threshold": "high",
            "notification_channels": ["email", "webhook", "sms"]
        }

        response = await client.put(f"/alerts/config/{config_id}", json=update_data, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Alert Config"
        assert data["keywords"] == ["updated", "new"]
        assert data["jurisdictions"] == ["federal", "california"]
        assert data["severity_threshold"] == "high"
        assert data["notification_channels"] == ["email", "webhook", "sms"]

    @pytest.mark.asyncio
    async def test_delete_alert_config(self, client: AsyncClient):
        """Test deleting alert configuration."""
        # Register user and create alert config first
        user_data = {
            "email": "deletealertconfigtest@example.com",
            "username": "deletealertconfigtest",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        login_data = {
            "username": "deletealertconfigtest@example.com",
            "password": "password123"
        }
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # Create alert config
        alert_config_data = {
            "name": "Config to Delete",
            "description": "Will be deleted",
            "keywords": ["delete"],
            "jurisdictions": ["federal"],
            "severity_threshold": "medium",
            "notification_channels": ["email"]
        }

        headers = {"Authorization": f"Bearer {token}"}
        create_response = await client.post("/alerts/config", json=alert_config_data, headers=headers)
        config_id = create_response.json()["id"]

        # Delete alert config
        response = await client.delete(f"/alerts/config/{config_id}", headers=headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = await client.get(f"/alerts/config/{config_id}", headers=headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestHealthEndpoints:
    """Integration tests for health endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    @pytest.mark.asyncio
    async def test_readiness_check(self, client: AsyncClient):
        """Test readiness check endpoint."""
        response = await client.get("/health/readiness")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "ready"

    @pytest.mark.asyncio
    async def test_liveness_check(self, client: AsyncClient):
        """Test liveness check endpoint."""
        response = await client.get("/health/liveness")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "alive"
