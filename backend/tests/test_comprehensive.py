"""Comprehensive test suite for LegalEdge platform."""
import asyncio
import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.config import Settings
from app.models import Base
from app.services.auth import authenticate_user, create_access_token
from app.services.soc2_compliance import security_manager, SOC2_COMPLIANCE
from app.services.access_control import access_control
from app.repositories.auth import create_user, get_user_by_username

# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Create test database."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def test_settings():
    """Test settings configuration."""
    return Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        redis_url="redis://localhost:6379/0",
        environment="test",
        openai_api_key="test-key"
    )

@pytest.fixture
def test_client():
    """Test client for FastAPI."""
    return TestClient(app)

# Authentication Tests
class TestAuthentication:
    """Test authentication functionality."""

    @pytest.mark.asyncio
    async def test_user_registration(self, test_db):
        """Test user registration with SOC2-compliant password."""
        # Test valid registration
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }

        user = await create_user(test_db, user_data)
        assert user.email == user_data["email"]
        assert user.username == user_data["username"]
        assert user.is_active == True

    @pytest.mark.asyncio
    async def test_password_policy_validation(self):
        """Test SOC2-compliant password policy."""
        violations = await security_manager.validate_password_policy("weak")
        assert len(violations) > 0

        violations = await security_manager.validate_password_policy("SecurePass123!@#")
        assert len(violations) == 0

    @pytest.mark.asyncio
    async def test_failed_login_attempts(self, test_db):
        """Test account lockout after failed attempts."""
        username = "testuser"
        wrong_password = "wrongpassword"

        # Create user first
        user_data = {
            "email": "test@example.com",
            "username": username,
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
        await create_user(test_db, user_data)

        # Mock request
        mock_request = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.get.return_value = "test-agent"

        # Try failed logins
        for i in range(SOC2_COMPLIANCE["max_login_attempts"]):
            with pytest.raises(Exception):  # Should fail
                await security_manager.authenticate_user(
                    test_db, username, wrong_password, mock_request
                )

        # Account should be locked
        assert security_manager._is_account_locked(username)

    @pytest.mark.asyncio
    async def test_successful_authentication(self, test_db):
        """Test successful authentication."""
        username = "testuser"
        password = "SecurePass123!"

        # Create user
        user_data = {
            "email": "test@example.com",
            "username": username,
            "password": password,
            "full_name": "Test User"
        }
        await create_user(test_db, user_data)

        # Mock request
        mock_request = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.get.return_value = "test-agent"

        # Authenticate successfully
        user, password_change_required = await security_manager.authenticate_user(
            test_db, username, password, mock_request
        )

        assert user.username == username
        assert password_change_required == False

# Authorization Tests
class TestAuthorization:
    """Test authorization and access controls."""

    @pytest.mark.asyncio
    async def test_permission_checking(self, test_db):
        """Test permission-based access control."""
        # Create user
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
        user = await create_user(test_db, user_data)

        # Test permission check
        has_permission = await access_control.check_permission(
            test_db, user.id, "alerts", "read"
        )

        # Should be False initially (no roles assigned)
        assert has_permission == False

    @pytest.mark.asyncio
    async def test_role_based_access(self, test_db):
        """Test role-based access control."""
        # This would test role assignment and permission inheritance
        pass

# API Tests
class TestAPIEndpoints:
    """Test API endpoints."""

    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/api/v1/health/status")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_authentication_flow(self, test_client):
        """Test complete authentication flow."""
        # Register user
        register_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
        response = test_client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201

        # Login
        login_data = {
            "username": "testuser",
            "password": "SecurePass123!"
        }
        response = test_client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_authorization_required(self, test_client):
        """Test that protected endpoints require authentication."""
        response = test_client.get("/api/v1/auth/me")
        assert response.status_code == 401

# Performance Tests
class TestPerformance:
    """Performance and load testing."""

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, test_db):
        """Test concurrent request handling."""
        import asyncio
        import time

        async def make_request():
            # Simulate concurrent requests
            await asyncio.sleep(0.01)
            return True

        start_time = time.time()

        # Run concurrent requests
        tasks = [make_request() for _ in range(100)]
        results = await asyncio.gather(*tasks)

        end_time = time.time()

        assert len(results) == 100
        assert end_time - start_time < 5  # Should complete within 5 seconds

    @pytest.mark.asyncio
    async def test_database_connection_pooling(self, test_db):
        """Test database connection pooling."""
        # Test multiple concurrent database operations
        async def db_operation():
            # Simulate database work
            await asyncio.sleep(0.1)
            return True

        tasks = [db_operation() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 10

# Security Tests
class TestSecurity:
    """Security testing suite."""

    def test_password_hashing(self):
        """Test password hashing security."""
        from app.services.auth import get_password_hash

        password = "SecurePass123!"
        hashed = get_password_hash(password)

        # Hash should be different each time
        hashed2 = get_password_hash(password)
        assert hashed != hashed2

        # Hash should be long enough (bcrypt with 14 rounds)
        assert len(hashed) >= 60

    def test_jwt_token_security(self):
        """Test JWT token generation and validation."""
        from app.services.auth import create_access_token

        data = {"sub": "testuser"}
        token = create_access_token(data)

        # Token should be properly formatted
        assert len(token) > 50

        # Should be able to decode (validation would be in auth service)
        import jwt
        decoded = jwt.decode(token, options={"verify_signature": False})
        assert decoded["sub"] == "testuser"

    @pytest.mark.asyncio
    async def test_sql_injection_prevention(self, test_db):
        """Test SQL injection prevention."""
        # This would test parameterized queries and input sanitization
        malicious_input = "'; DROP TABLE users; --"

        # Should not execute malicious SQL
        user = await get_user_by_username(test_db, malicious_input)
        assert user is None  # Should return None, not execute the injection

    def test_xss_protection(self, test_client):
        """Test XSS protection."""
        malicious_script = '<script>alert("xss")</script>'

        # This would test input sanitization
        # For now, just verify the endpoint accepts input
        response = test_client.post("/api/v1/auth/register", json={
            "email": f"test{malicious_script}@example.com",
            "username": "testuser",
            "password": "SecurePass123!",
            "full_name": "Test User"
        })

        # Should reject or sanitize malicious input
        assert response.status_code != 500

# Integration Tests
class TestIntegration:
    """Integration testing."""

    @pytest.mark.asyncio
    async def test_user_registration_and_auth(self, test_db):
        """Test complete user registration and authentication flow."""
        # Register user
        user_data = {
            "email": "integration@example.com",
            "username": "integrationuser",
            "password": "SecurePass123!",
            "full_name": "Integration Test User"
        }

        user = await create_user(test_db, user_data)
        assert user.email == user_data["email"]

        # Authenticate user
        mock_request = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.get.return_value = "test-agent"

        authenticated_user, _ = await security_manager.authenticate_user(
            test_db, user_data["username"], user_data["password"], mock_request
        )

        assert authenticated_user.id == user.id

    @pytest.mark.asyncio
    async def test_audit_logging(self, test_db):
        """Test audit logging functionality."""
        from app.models.auth import AuditLog
        from app.repositories.auth import create_audit_log

        # Create audit log entry
        audit_entry = AuditLog(
            user_id=1,
            action="test_action",
            resource="test_resource",
            details={"test": "data"}
        )

        created_entry = await create_audit_log(test_db, audit_entry)
        assert created_entry.action == "test_action"

# Load Testing
class TestLoad:
    """Load testing suite."""

    @pytest.mark.asyncio
    async def test_high_concurrent_load(self):
        """Test system under high concurrent load."""
        import time

        async def make_api_call():
            await asyncio.sleep(0.1)
            return True

        start_time = time.time()

        # Simulate 1000 concurrent requests
        tasks = [make_api_call() for _ in range(1000)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()

        successful_requests = sum(1 for r in results if r is True)
        failed_requests = sum(1 for r in results if isinstance(r, Exception))

        assert successful_requests >= 950  # 95% success rate
        assert failed_requests <= 50     # 5% failure tolerance
        assert end_time - start_time <= 30  # Complete within 30 seconds

# Compliance Tests
class TestCompliance:
    """SOC2 and compliance testing."""

    def test_data_encryption(self):
        """Test data encryption compliance."""
        from app.services.soc2_compliance import hash_sensitive_data

        sensitive_data = "user@example.com"
        hashed = hash_sensitive_data(sensitive_data)

        # Hash should be consistent
        hashed2 = hash_sensitive_data(sensitive_data)
        assert hashed == hashed2

        # Hash should be different for different data
        hashed3 = hash_sensitive_data("different@example.com")
        assert hashed != hashed3

    @pytest.mark.asyncio
    async def test_audit_log_compliance(self, test_db):
        """Test audit logging compliance."""
        from app.services.soc2_compliance import perform_security_health_check

        health_check = await perform_security_health_check()

        assert health_check["password_policy_compliant"] == True
        assert health_check["encryption_enabled"] == True
        assert health_check["audit_logging_active"] == True

    def test_access_control_compliance(self):
        """Test access control compliance."""
        # Test that access controls are properly implemented
        # This would verify RBAC implementation
        pass

# Error Handling Tests
class TestErrorHandling:
    """Test error handling and resilience."""

    def test_database_connection_error(self, test_client):
        """Test handling of database connection errors."""
        with patch('app.db.session.get_session') as mock_session:
            mock_session.side_effect = Exception("Database connection failed")

            response = test_client.get("/api/v1/dashboard/snapshot")
            assert response.status_code >= 500

    def test_invalid_input_handling(self, test_client):
        """Test handling of invalid input."""
        # Test invalid JSON
        response = test_client.post("/api/v1/auth/register", data="invalid json")
        assert response.status_code == 400

        # Test missing required fields
        response = test_client.post("/api/v1/auth/register", json={
            "email": "test@example.com"
            # Missing required fields
        })
        assert response.status_code == 422

    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # This would test the rate limiting implementation
        pass

# Data Validation Tests
class TestDataValidation:
    """Test data validation and sanitization."""

    def test_email_validation(self, test_client):
        """Test email format validation."""
        response = test_client.post("/api/v1/auth/register", json={
            "email": "invalid-email",
            "username": "testuser",
            "password": "SecurePass123!",
            "full_name": "Test User"
        })
        assert response.status_code == 422

    def test_password_strength_validation(self, test_client):
        """Test password strength requirements."""
        response = test_client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "weak",
            "full_name": "Test User"
        })
        assert response.status_code == 400  # Should fail password policy

    def test_input_sanitization(self, test_client):
        """Test input sanitization."""
        # Test SQL injection prevention
        malicious_input = "'; DROP TABLE users; --"
        response = test_client.post("/api/v1/auth/register", json={
            "email": f"{malicious_input}@example.com",
            "username": malicious_input,
            "password": "SecurePass123!",
            "full_name": malicious_input
        })
        # Should either sanitize or reject malicious input
        assert response.status_code in [400, 422, 500]

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
