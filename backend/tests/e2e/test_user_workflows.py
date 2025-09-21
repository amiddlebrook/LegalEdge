"""End-to-end tests for critical user workflows."""

import pytest
from httpx import AsyncClient
from fastapi import status
from datetime import datetime, timedelta
import asyncio


class TestUserRegistrationWorkflow:
    """E2E tests for user registration workflow."""

    @pytest.mark.asyncio
    async def test_complete_user_registration_flow(self, client: AsyncClient):
        """Test complete user registration and verification flow."""
        # 1. Register user
        user_data = {
            "email": "e2euser@example.com",
            "username": "e2euser",
            "password": "password123",
            "full_name": "E2E Test User"
        }

        register_response = await client.post("/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        user_data_response = register_response.json()
        assert user_data_response["email"] == "e2euser@example.com"
        assert user_data_response["username"] == "e2euser"
        assert "id" in user_data_response

        # 2. Login with new credentials
        login_data = {
            "username": "e2euser@example.com",
            "password": "password123"
        }

        login_response = await client.post("/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        login_data_response = login_response.json()
        assert "access_token" in login_data_response
        assert "refresh_token" in login_data_response
        assert login_data_response["token_type"] == "bearer"

        token = login_data_response["access_token"]

        # 3. Get current user info
        headers = {"Authorization": f"Bearer {token}"}
        me_response = await client.get("/auth/me", headers=headers)
        assert me_response.status_code == status.HTTP_200_OK
        me_data = me_response.json()
        assert me_data["email"] == "e2euser@example.com"
        assert me_data["username"] == "e2euser"
        assert me_data["is_active"] is True

        # 4. Test logout
        logout_response = await client.post("/auth/logout", headers=headers)
        assert logout_response.status_code == status.HTTP_200_OK

        # 5. Verify token is invalidated (should fail after logout)
        me_response_after_logout = await client.get("/auth/me", headers=headers)
        assert me_response_after_logout.status_code == status.HTTP_401_UNAUTHORIZED


class TestPortfolioManagementWorkflow:
    """E2E tests for portfolio management workflow."""

    @pytest.mark.asyncio
    async def test_complete_portfolio_management_flow(self, client: AsyncClient):
        """Test complete portfolio creation, update, and deletion flow."""
        # 1. Register and login user
        user_data = {
            "email": "portfolioworkflow@example.com",
            "username": "portfolioworkflow",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        login_data = {
            "username": "portfolioworkflow@example.com",
            "password": "password123"
        }
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create portfolio
        portfolio_data = {
            "name": "Tech Growth Portfolio",
            "description": "Portfolio focused on technology companies",
            "tickers": ["AAPL", "MSFT", "GOOGL", "NVDA"]
        }

        create_response = await client.post("/portfolios/", json=portfolio_data, headers=headers)
        assert create_response.status_code == status.HTTP_201_CREATED
        portfolio = create_response.json()
        portfolio_id = portfolio["id"]
        assert portfolio["name"] == "Tech Growth Portfolio"
        assert portfolio["tickers"] == ["AAPL", "MSFT", "GOOGL", "NVDA"]

        # 3. Get portfolio details
        get_response = await client.get(f"/portfolios/{portfolio_id}", headers=headers)
        assert get_response.status_code == status.HTTP_200_OK
        retrieved_portfolio = get_response.json()
        assert retrieved_portfolio["id"] == portfolio_id
        assert retrieved_portfolio["name"] == "Tech Growth Portfolio"

        # 4. Update portfolio
        update_data = {
            "name": "Updated Tech Growth Portfolio",
            "description": "Updated portfolio description",
            "tickers": ["TSLA", "NVDA", "AMD", "INTC"]
        }

        update_response = await client.put(f"/portfolios/{portfolio_id}", json=update_data, headers=headers)
        assert update_response.status_code == status.HTTP_200_OK
        updated_portfolio = update_response.json()
        assert updated_portfolio["name"] == "Updated Tech Growth Portfolio"
        assert updated_portfolio["tickers"] == ["TSLA", "NVDA", "AMD", "INTC"]

        # 5. List user's portfolios
        list_response = await client.get("/portfolios/", headers=headers)
        assert list_response.status_code == status.HTTP_200_OK
        portfolios = list_response.json()
        assert len(portfolios) >= 1
        assert any(p["id"] == portfolio_id for p in portfolios)

        # 6. Delete portfolio
        delete_response = await client.delete(f"/portfolios/{portfolio_id}", headers=headers)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # 7. Verify portfolio is deleted
        get_after_delete = await client.get(f"/portfolios/{portfolio_id}", headers=headers)
        assert get_after_delete.status_code == status.HTTP_404_NOT_FOUND


class TestAlertsWorkflow:
    """E2E tests for alerts workflow."""

    @pytest.mark.asyncio
    async def test_complete_alerts_workflow(self, client: AsyncClient):
        """Test complete alerts creation, configuration, and notification flow."""
        # 1. Register and login user
        user_data = {
            "email": "alertsworkflow@example.com",
            "username": "alertsworkflow",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        login_data = {
            "username": "alertsworkflow@example.com",
            "password": "password123"
        }
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create alert configuration
        alert_config_data = {
            "name": "AI Regulation Alerts",
            "description": "Alerts for AI regulation legislation",
            "keywords": ["artificial intelligence", "machine learning", "AI regulation"],
            "jurisdictions": ["federal", "california"],
            "severity_threshold": "medium",
            "notification_channels": ["email", "webhook"]
        }

        config_response = await client.post("/alerts/config", json=alert_config_data, headers=headers)
        assert config_response.status_code == status.HTTP_201_CREATED
        alert_config = config_response.json()
        config_id = alert_config["id"]
        assert alert_config["name"] == "AI Regulation Alerts"
        assert "artificial intelligence" in alert_config["keywords"]

        # 3. Get user's alert configurations
        configs_response = await client.get("/alerts/config", headers=headers)
        assert configs_response.status_code == status.HTTP_200_OK
        configs = configs_response.json()
        assert len(configs) >= 1
        assert any(c["id"] == config_id for c in configs)

        # 4. Update alert configuration
        update_data = {
            "name": "Updated AI Regulation Alerts",
            "description": "Updated AI regulation alerts",
            "keywords": ["artificial intelligence", "machine learning", "neural networks"],
            "jurisdictions": ["federal", "california", "new_york"],
            "severity_threshold": "high",
            "notification_channels": ["email", "webhook", "sms"]
        }

        update_response = await client.put(f"/alerts/config/{config_id}", json=update_data, headers=headers)
        assert update_response.status_code == status.HTTP_200_OK
        updated_config = update_response.json()
        assert updated_config["name"] == "Updated AI Regulation Alerts"
        assert updated_config["severity_threshold"] == "high"
        assert "sms" in updated_config["notification_channels"]

        # 5. Get alerts feed (may be empty but should not error)
        feed_response = await client.get("/alerts/feed", headers=headers)
        assert feed_response.status_code == status.HTTP_200_OK
        alerts = feed_response.json()
        assert isinstance(alerts, list)

        # 6. Delete alert configuration
        delete_response = await client.delete(f"/alerts/config/{config_id}", headers=headers)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # 7. Verify configuration is deleted
        get_after_delete = await client.get(f"/alerts/config/{config_id}", headers=headers)
        assert get_after_delete.status_code == status.HTTP_404_NOT_FOUND


class TestLegislationWorkflow:
    """E2E tests for legislation workflow."""

    @pytest.mark.asyncio
    async def test_legislation_search_and_analysis_workflow(self, client: AsyncClient):
        """Test legislation search, filtering, and analysis workflow."""
        # 1. Search for legislation
        search_params = {
            "query": "artificial intelligence",
            "jurisdiction": "federal",
            "limit": 10
        }

        search_response = await client.get("/legislation/search", params=search_params)
        assert search_response.status_code == status.HTTP_200_OK
        legislation_list = search_response.json()
        assert isinstance(legislation_list, list)

        # If there are results, test getting individual legislation
        if legislation_list:
            legislation_id = legislation_list[0]["id"]

            # 2. Get specific legislation details
            detail_response = await client.get(f"/legislation/{legislation_id}")
            if detail_response.status_code == status.HTTP_200_OK:
                legislation_detail = detail_response.json()
                assert legislation_detail["id"] == legislation_id
                assert "title" in legislation_detail
                assert "summary" in legislation_detail

            # 3. Get legislation by topics
            topics_response = await client.get("/legislation/topics/artificial intelligence,technology")
            assert topics_response.status_code == status.HTTP_200_OK
            topics_legislation = topics_response.json()
            assert isinstance(topics_legislation, list)

            # 4. Get legislation by jurisdiction
            jurisdiction_response = await client.get("/legislation/jurisdiction/federal")
            assert jurisdiction_response.status_code == status.HTTP_200_OK
            jurisdiction_legislation = jurisdiction_response.json()
            assert isinstance(jurisdiction_legislation, list)


class TestDashboardWorkflow:
    """E2E tests for dashboard workflow."""

    @pytest.mark.asyncio
    async def test_dashboard_overview_workflow(self, client: AsyncClient):
        """Test dashboard overview and insights workflow."""
        # 1. Register and login user
        user_data = {
            "email": "dashboardworkflow@example.com",
            "username": "dashboardworkflow",
            "password": "password123"
        }
        await client.post("/auth/register", json=user_data)

        login_data = {
            "username": "dashboardworkflow@example.com",
            "password": "password123"
        }
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get dashboard overview
        overview_response = await client.get("/dashboard/overview", headers=headers)
        assert overview_response.status_code == status.HTTP_200_OK
        overview = overview_response.json()
        assert isinstance(overview, dict)
        assert "total_portfolios" in overview or "message" in overview

        # 3. Get coverage metrics
        coverage_response = await client.get("/dashboard/coverage", headers=headers)
        assert coverage_response.status_code == status.HTTP_200_OK
        coverage = coverage_response.json()
        assert isinstance(coverage, dict) or isinstance(coverage, list)

        # 4. Get opportunities
        opportunities_response = await client.get("/dashboard/opportunities", headers=headers)
        assert opportunities_response.status_code == status.HTTP_200_OK
        opportunities = opportunities_response.json()
        assert isinstance(opportunities, list)


class TestSystemHealthWorkflow:
    """E2E tests for system health workflow."""

    @pytest.mark.asyncio
    async def test_system_health_checks(self, client: AsyncClient):
        """Test system health check endpoints."""
        # 1. Health check
        health_response = await client.get("/health/")
        assert health_response.status_code == status.HTTP_200_OK
        health_data = health_response.json()
        assert health_data["status"] == "healthy"
        assert "timestamp" in health_data
        assert "version" in health_data

        # 2. Readiness check
        readiness_response = await client.get("/health/readiness")
        assert readiness_response.status_code == status.HTTP_200_OK
        readiness_data = readiness_response.json()
        assert readiness_data["status"] == "ready"

        # 3. Liveness check
        liveness_response = await client.get("/health/liveness")
        assert liveness_response.status_code == status.HTTP_200_OK
        liveness_data = liveness_response.json()
        assert liveness_data["status"] == "alive"


class TestErrorHandlingWorkflow:
    """E2E tests for error handling workflows."""

    @pytest.mark.asyncio
    async def test_authentication_error_handling(self, client: AsyncClient):
        """Test authentication error handling."""
        # 1. Try to access protected endpoint without auth
        protected_response = await client.get("/auth/me")
        assert protected_response.status_code == status.HTTP_401_UNAUTHORIZED

        # 2. Try to login with wrong credentials
        wrong_login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        wrong_login_response = await client.post("/auth/login", data=wrong_login_data)
        assert wrong_login_response.status_code == status.HTTP_401_UNAUTHORIZED

        # 3. Try to use invalid token
        invalid_headers = {"Authorization": "Bearer invalid.token.here"}
        invalid_token_response = await client.get("/auth/me", headers=invalid_headers)
        assert invalid_token_response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_resource_not_found_handling(self, client: AsyncClient):
        """Test 404 error handling."""
        # 1. Try to get non-existent portfolio
        not_found_response = await client.get("/portfolios/non-existent-id")
        assert not_found_response.status_code == status.HTTP_404_NOT_FOUND

        # 2. Try to get non-existent legislation
        legislation_not_found = await client.get("/legislation/non-existent-bill")
        assert legislation_not_found.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_validation_error_handling(self, client: AsyncClient):
        """Test validation error handling."""
        # 1. Try to register with invalid email
        invalid_user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "password123"
        }
        invalid_register_response = await client.post("/auth/register", json=invalid_user_data)
        assert invalid_register_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # 2. Try to create portfolio with invalid data
        invalid_portfolio_data = {
            "name": "",  # Invalid empty name
            "description": "Test portfolio",
            "tickers": []
        }
        invalid_portfolio_response = await client.post("/portfolios/", json=invalid_portfolio_data)
        assert invalid_portfolio_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestConcurrentUserWorkflow:
    """E2E tests for concurrent user workflows."""

    @pytest.mark.asyncio
    async def test_multiple_users_concurrent_operations(self, client: AsyncClient):
        """Test multiple users performing operations concurrently."""
        async def user_workflow(user_id: int):
            """Simulate a user workflow."""
            # Register user
            user_data = {
                "email": f"concurrentuser{user_id}@example.com",
                "username": f"concurrentuser{user_id}",
                "password": "password123"
            }
            await client.post("/auth/register", json=user_data)

            # Login
            login_data = {
                "username": f"concurrentuser{user_id}@example.com",
                "password": "password123"
            }
            login_response = await client.post("/auth/login", data=login_data)
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Create portfolio
            portfolio_data = {
                "name": f"Concurrent Portfolio {user_id}",
                "description": f"Portfolio for concurrent user {user_id}",
                "tickers": ["AAPL", "MSFT"]
            }
            await client.post("/portfolios/", json=portfolio_data, headers=headers)

            # Create alert config
            alert_config_data = {
                "name": f"Concurrent Alert {user_id}",
                "description": f"Alert config for concurrent user {user_id}",
                "keywords": ["test", "concurrent"],
                "jurisdictions": ["federal"],
                "severity_threshold": "medium",
                "notification_channels": ["email"]
            }
            await client.post("/alerts/config", json=alert_config_data, headers=headers)

            return f"user_{user_id}_completed"

        # Run multiple users concurrently
        tasks = [user_workflow(i) for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all workflows completed
        assert len(results) == 5
        assert all("completed" in str(result) for result in results)

        # Verify all users were created
        for i in range(5):
            # Check if user can login (this verifies they exist)
            login_data = {
                "username": f"concurrentuser{i}@example.com",
                "password": "password123"
            }
            login_response = await client.post("/auth/login", data=login_data)
            assert login_response.status_code == status.HTTP_200_OK
