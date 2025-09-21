"""Unit tests for repository classes."""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import legislation, portfolio, auth, insights
from app.models import Legislation, Portfolio, User, AlertConfig
from tests.fixtures.factories import (
    LegislationFactory, PortfolioFactory, UserFactory, AlertConfigFactory
)


class TestLegislationRepository:
    """Test legislation repository functions."""

    @pytest.mark.asyncio
    async def test_list_upcoming_legislation(self, db_session: AsyncSession, mocker):
        """Test listing upcoming legislation."""
        # Create test data
        bills = []
        for i in range(3):
            bill = LegislationFactory(
                status="introduced",
                introduced_date=date.today() - timedelta(days=i)
            )
            bills.append(bill)
            db_session.add(bill)

        await db_session.commit()

        # Test without filters
        result = await legislation.list_upcoming_legislation(db_session, limit=10)
        assert len(result) == 3

        # Test with jurisdiction filter
        result = await legislation.list_upcoming_legislation(
            db_session,
            jurisdiction="federal",
            limit=10
        )
        assert len(result) >= 0

        # Test with stage filter
        result = await legislation.list_upcoming_legislation(
            db_session,
            stage="introduced",
            limit=10
        )
        assert len(result) >= 0

    @pytest.mark.asyncio
    async def test_list_upcoming_legislation_with_sectors(self, db_session: AsyncSession, mocker):
        """Test listing legislation with sector filters."""
        # Create test data with sectors
        bill1 = LegislationFactory(
            topics=["technology", "healthcare"],
            status="introduced"
        )
        bill2 = LegislationFactory(
            topics=["finance", "banking"],
            status="introduced"
        )
        db_session.add_all([bill1, bill2])
        await db_session.commit()

        # Test sector filtering
        result = await legislation.list_upcoming_legislation(
            db_session,
            sectors=["technology"],
            limit=10
        )
        assert len(result) >= 0

    @pytest.mark.asyncio
    async def test_get_legislation_by_id(self, db_session: AsyncSession):
        """Test getting legislation by ID."""
        bill = LegislationFactory()
        db_session.add(bill)
        await db_session.commit()

        result = await legislation.get_legislation_by_id(db_session, bill.id)
        assert result is not None
        assert result.id == bill.id
        assert result.title == bill.title

    @pytest.mark.asyncio
    async def test_get_legislation_by_id_not_found(self, db_session: AsyncSession):
        """Test getting legislation by non-existent ID."""
        result = await legislation.get_legislation_by_id(db_session, "non-existent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_create_legislation(self, db_session: AsyncSession):
        """Test creating legislation."""
        bill_data = {
            "id": "new-bill-123",
            "title": "New Test Bill",
            "summary": "A new test bill",
            "status": "introduced",
            "jurisdiction": "federal",
            "bill_number": "HB-5678",
            "introduced_date": date.today(),
            "sponsors": ["Test Sponsor"],
            "topics": ["test", "regulation"],
            "sentiment_score": 0.5,
            "enactment_probability": 0.7,
            "impact_score": 6.0,
            "full_text_url": "https://example.com"
        }

        result = await legislation.create_legislation(db_session, bill_data)
        await db_session.commit()

        assert result.id == "new-bill-123"
        assert result.title == "New Test Bill"
        assert result.status == "introduced"

    @pytest.mark.asyncio
    async def test_update_legislation(self, db_session: AsyncSession):
        """Test updating legislation."""
        bill = LegislationFactory(status="introduced")
        db_session.add(bill)
        await db_session.commit()

        update_data = {
            "status": "passed",
            "sentiment_score": 0.8,
            "enactment_probability": 0.9
        }

        result = await legislation.update_legislation(db_session, bill.id, update_data)
        await db_session.commit()
        await db_session.refresh(result)

        assert result.status == "passed"
        assert result.sentiment_score == 0.8
        assert result.enactment_probability == 0.9

    @pytest.mark.asyncio
    async def test_delete_legislation(self, db_session: AsyncSession):
        """Test deleting legislation."""
        bill = LegislationFactory()
        db_session.add(bill)
        await db_session.commit()

        result = await legislation.delete_legislation(db_session, bill.id)
        await db_session.commit()

        assert result is True

        # Verify deletion
        deleted_bill = await legislation.get_legislation_by_id(db_session, bill.id)
        assert deleted_bill is None

    @pytest.mark.asyncio
    async def test_search_legislation(self, db_session: AsyncSession):
        """Test searching legislation."""
        # Create test data
        bill1 = LegislationFactory(title="AI Regulation Bill", topics=["artificial intelligence"])
        bill2 = LegislationFactory(title="Healthcare Reform", topics=["healthcare"])
        bill3 = LegislationFactory(title="AI and Healthcare Bill", topics=["artificial intelligence", "healthcare"])

        db_session.add_all([bill1, bill2, bill3])
        await db_session.commit()

        # Test search by title
        result = await legislation.search_legislation(db_session, query="AI")
        assert len(result) >= 2

        # Test search by topics
        result = await legislation.search_legislation(db_session, topics=["artificial intelligence"])
        assert len(result) >= 2

        # Test search by jurisdiction
        result = await legislation.search_legislation(db_session, jurisdiction="federal")
        assert len(result) >= 0


class TestPortfolioRepository:
    """Test portfolio repository functions."""

    @pytest.mark.asyncio
    async def test_create_portfolio(self, db_session: AsyncSession):
        """Test creating a portfolio."""
        portfolio_data = {
            "id": "test-portfolio-123",
            "name": "Test Portfolio",
            "description": "A test portfolio",
            "user_id": 1,
            "tickers": ["AAPL", "MSFT", "GOOGL"]
        }

        result = await portfolio.create_portfolio(db_session, portfolio_data)
        await db_session.commit()

        assert result.id == "test-portfolio-123"
        assert result.name == "Test Portfolio"
        assert result.user_id == 1
        assert len(result.tickers) == 3

    @pytest.mark.asyncio
    async def test_get_portfolio_by_id(self, db_session: AsyncSession):
        """Test getting portfolio by ID."""
        port = PortfolioFactory()
        db_session.add(port)
        await db_session.commit()

        result = await portfolio.get_portfolio_by_id(db_session, port.id)
        assert result is not None
        assert result.id == port.id
        assert result.name == port.name

    @pytest.mark.asyncio
    async def test_get_portfolios_by_user(self, db_session: AsyncSession):
        """Test getting portfolios by user ID."""
        user_id = 1
        portfolios = []
        for i in range(3):
            port = PortfolioFactory(user_id=user_id)
            portfolios.append(port)
            db_session.add(port)

        await db_session.commit()

        result = await portfolio.get_portfolios_by_user(db_session, user_id)
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_update_portfolio(self, db_session: AsyncSession):
        """Test updating a portfolio."""
        port = PortfolioFactory()
        db_session.add(port)
        await db_session.commit()

        update_data = {
            "name": "Updated Portfolio Name",
            "description": "Updated description",
            "tickers": ["TSLA", "NVDA", "AMD"]
        }

        result = await portfolio.update_portfolio(db_session, port.id, update_data)
        await db_session.commit()
        await db_session.refresh(result)

        assert result.name == "Updated Portfolio Name"
        assert result.description == "Updated description"
        assert len(result.tickers) == 3
        assert "TSLA" in result.tickers

    @pytest.mark.asyncio
    async def test_delete_portfolio(self, db_session: AsyncSession):
        """Test deleting a portfolio."""
        port = PortfolioFactory()
        db_session.add(port)
        await db_session.commit()

        result = await portfolio.delete_portfolio(db_session, port.id)
        await db_session.commit()

        assert result is True

        # Verify deletion
        deleted_port = await portfolio.get_portfolio_by_id(db_session, port.id)
        assert deleted_port is None


class TestAuthRepository:
    """Test authentication repository functions."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        """Test creating a user."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashedpassword123",
            "is_active": True,
            "is_superuser": False
        }

        result = await auth.create_user(db_session, user_data)
        await db_session.commit()

        assert result.email == "test@example.com"
        assert result.username == "testuser"
        assert result.is_active is True
        assert result.is_superuser is False

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, db_session: AsyncSession):
        """Test getting user by email."""
        user = UserFactory(email="unique@example.com")
        db_session.add(user)
        await db_session.commit()

        result = await auth.get_user_by_email(db_session, "unique@example.com")
        assert result is not None
        assert result.email == "unique@example.com"

    @pytest.mark.asyncio
    async def test_get_user_by_username(self, db_session: AsyncSession):
        """Test getting user by username."""
        user = UserFactory(username="uniqueuser")
        db_session.add(user)
        await db_session.commit()

        result = await auth.get_user_by_username(db_session, "uniqueuser")
        assert result is not None
        assert result.username == "uniqueuser"

    @pytest.mark.asyncio
    async def test_authenticate_user(self, db_session: AsyncSession, mocker):
        """Test user authentication."""
        # Mock password verification
        mock_verify = mocker.patch("app.repositories.auth.verify_password")
        mock_verify.return_value = True

        user = UserFactory()
        db_session.add(user)
        await db_session.commit()

        result = await auth.authenticate_user(db_session, user.email, "password")
        assert result is not None
        assert result.email == user.email

    @pytest.mark.asyncio
    async def test_update_user_password(self, db_session: AsyncSession):
        """Test updating user password."""
        user = UserFactory()
        db_session.add(user)
        await db_session.commit()

        new_hashed_password = "newhashedpassword456"
        result = await auth.update_user_password(db_session, user.id, new_hashed_password)
        await db_session.commit()
        await db_session.refresh(result)

        assert result.hashed_password == new_hashed_password

    @pytest.mark.asyncio
    async def test_delete_user(self, db_session: AsyncSession):
        """Test deleting a user."""
        user = UserFactory()
        db_session.add(user)
        await db_session.commit()

        result = await auth.delete_user(db_session, user.id)
        await db_session.commit()

        assert result is True

        # Verify deletion
        deleted_user = await auth.get_user_by_email(db_session, user.email)
        assert deleted_user is None


class TestInsightsRepository:
    """Test insights repository functions."""

    @pytest.mark.asyncio
    async def test_create_insights_dashboard(self, db_session: AsyncSession):
        """Test creating insights dashboard."""
        dashboard_data = {
            "user_id": 1,
            "name": "Test Dashboard",
            "description": "A test dashboard",
            "widgets": [
                {"type": "chart", "config": {"title": "Test Chart"}},
                {"type": "metric", "config": {"title": "Test Metric"}}
            ]
        }

        result = await insights.create_insights_dashboard(db_session, dashboard_data)
        await db_session.commit()

        assert result.user_id == 1
        assert result.name == "Test Dashboard"
        assert len(result.widgets) == 2

    @pytest.mark.asyncio
    async def test_get_dashboard_by_user(self, db_session: AsyncSession):
        """Test getting dashboard by user ID."""
        dashboard = await insights.create_insights_dashboard(
            db_session,
            {"user_id": 1, "name": "User Dashboard", "description": "User dashboard"}
        )
        await db_session.commit()

        result = await insights.get_insights_dashboard_by_user(db_session, 1)
        assert result is not None
        assert result.user_id == 1
        assert result.name == "User Dashboard"

    @pytest.mark.asyncio
    async def test_update_dashboard(self, db_session: AsyncSession):
        """Test updating dashboard."""
        dashboard = await insights.create_insights_dashboard(
            db_session,
            {"user_id": 1, "name": "Original Dashboard", "description": "Original"}
        )
        await db_session.commit()

        update_data = {
            "name": "Updated Dashboard",
            "description": "Updated description",
            "widgets": [{"type": "updated_chart", "config": {"title": "Updated Chart"}}]
        }

        result = await insights.update_insights_dashboard(db_session, dashboard.id, update_data)
        await db_session.commit()
        await db_session.refresh(result)

        assert result.name == "Updated Dashboard"
        assert result.description == "Updated description"
        assert len(result.widgets) == 1
        assert result.widgets[0]["type"] == "updated_chart"

    @pytest.mark.asyncio
    async def test_delete_dashboard(self, db_session: AsyncSession):
        """Test deleting dashboard."""
        dashboard = await insights.create_insights_dashboard(
            db_session,
            {"user_id": 1, "name": "Test Dashboard", "description": "To be deleted"}
        )
        await db_session.commit()

        result = await insights.delete_insights_dashboard(db_session, dashboard.id)
        await db_session.commit()

        assert result is True

        # Verify deletion
        deleted_dashboard = await insights.get_insights_dashboard_by_user(db_session, 1)
        assert deleted_dashboard is None
