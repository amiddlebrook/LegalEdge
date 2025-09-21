"""Test-specific configuration and fixtures."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.main import app


@pytest_asyncio.fixture
async def test_db_session():
    """Create a test database session."""
    # This will be overridden by the main conftest.py db_session fixture
    pass


@pytest.fixture
def authenticated_client(client):
    """Create an authenticated test client."""
    # Add authentication headers
    client.headers.update({
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    })
    return client


@pytest.fixture
def admin_client(client):
    """Create an admin test client."""
    client.headers.update({
        "Authorization": "Bearer admin-token",
        "Content-Type": "application/json",
        "X-User-Role": "admin"
    })
    return client
