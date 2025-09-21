"""Shared pytest configuration and fixtures."""

import asyncio
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.session import get_db
from app.main import app
from app.models import Base


# Test database configuration
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///./test.db")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {},
        poolclass=StaticPool,
        echo=False,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_db(test_engine):
    """Create test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(test_engine, test_db):
    """Create a fresh database session for a test."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    """Create a test client with database dependency override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_settings():
    """Mock application settings for testing."""
    return {
        "database_url": TEST_DATABASE_URL,
        "redis_url": "redis://localhost:6379/1",
        "celery_broker_url": "redis://localhost:6379/2",
        "celery_result_backend": "redis://localhost:6379/3",
        "secret_key": "test-secret-key-for-testing-only",
        "algorithm": "HS256",
        "access_token_expire_minutes": 30,
        "refresh_token_expire_days": 7,
        "rate_limit_per_minute": 100,
        "aws_region": "us-east-1",
        "s3_bucket_name": "test-bucket",
        "sns_topic_arn": "arn:aws:sns:us-east-1:123456789012:test-topic",
    }


@pytest.fixture
def sample_legislation_data():
    """Sample legislation data for testing."""
    return {
        "id": "test-bill-123",
        "title": "Test Bill for AI Regulation",
        "summary": "A test bill about regulating artificial intelligence",
        "status": "introduced",
        "introduced_date": "2024-01-15",
        "jurisdiction": "federal",
        "bill_number": "HB-1234",
        "sponsors": ["Rep. John Doe"],
        "committees": ["Committee on Science, Space, and Technology"],
        "topics": ["artificial intelligence", "technology regulation"],
        "full_text_url": "https://example.com/bill-text",
    }


@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for testing."""
    return {
        "id": "test-portfolio-456",
        "name": "Tech Growth Portfolio",
        "description": "Portfolio focused on technology companies",
        "holdings": [
            {"ticker": "AAPL", "shares": 100, "value": 15000},
            {"ticker": "MSFT", "shares": 50, "value": 20000},
            {"ticker": "GOOGL", "shares": 25, "value": 7500},
        ],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-15T00:00:00Z",
    }


@pytest.fixture
def sample_alert_config():
    """Sample alert configuration for testing."""
    return {
        "id": "test-alert-789",
        "name": "AI Regulation Alerts",
        "description": "Alerts for AI-related legislation",
        "keywords": ["artificial intelligence", "machine learning", "AI regulation"],
        "jurisdictions": ["federal", "california"],
        "severity_threshold": "medium",
        "notification_channels": ["email", "webhook"],
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture(autouse=True)
def mock_redis(mocker):
    """Mock Redis client for all tests."""
    mock_redis_client = mocker.Mock()
    mock_redis_client.get.return_value = None
    mock_redis_client.set.return_value = True
    mock_redis_client.delete.return_value = True
    mock_redis_client.exists.return_value = False
    mock_redis_client.expire.return_value = True

    mocker.patch("app.core.redis.get_redis_client", return_value=mock_redis_client)
    return mock_redis_client


@pytest.fixture(autouse=True)
def mock_s3(mocker):
    """Mock S3 client for all tests."""
    mock_s3_client = mocker.Mock()
    mock_s3_client.upload_fileobj.return_value = None
    mock_s3_client.download_fileobj.return_value = None
    mock_s3_client.delete_object.return_value = None
    mock_s3_client.head_object.return_value = {"ContentLength": 1024}

    mocker.patch("app.utils.s3.get_s3_client", return_value=mock_s3_client)
    return mock_s3_client


@pytest.fixture(autouse=True)
def mock_celery(mocker):
    """Mock Celery app for all tests."""
    mock_celery_app = mocker.Mock()
    mock_celery_app.send_task.return_value = mocker.Mock(id="test-task-id")

    mocker.patch("app.celery_app.celery_app", mock_celery_app)
    return mock_celery_app


@pytest.fixture
def mock_external_api(mocker):
    """Mock external API calls."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_response.raise_for_status.return_value = None

    return mocker.patch("httpx.AsyncClient.get", return_value=mock_response)
