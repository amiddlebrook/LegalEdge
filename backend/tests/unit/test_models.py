"""Unit tests for SQLAlchemy models."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    User, Legislation, Portfolio, Alert, AlertConfig,
    LegislationSentiment, MarketForecast, Opportunity, ConflictScore
)
from tests.fixtures.factories import (
    UserFactory, LegislationFactory, PortfolioFactory,
    AlertFactory, AlertConfigFactory, LegislationSentimentFactory,
    MarketForecastFactory, OpportunityFactory, ConflictScoreFactory
)


class TestUser:
    """Test User model."""

    @pytest.mark.asyncio
    async def test_user_creation(self, db_session: AsyncSession):
        """Test creating a user."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123",
            is_active=True,
            is_superuser=False
        )

        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.is_superuser is False
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    @pytest.mark.asyncio
    async def test_user_factory(self, db_session: AsyncSession):
        """Test User factory."""
        user = UserFactory()
        db_session.add(user)
        await db_session.commit()

        assert user.id is not None
        assert user.email
        assert user.username
        assert user.is_active is True


class TestLegislation:
    """Test Legislation model."""

    @pytest.mark.asyncio
    async def test_legislation_creation(self, db_session: AsyncSession):
        """Test creating legislation."""
        legislation = Legislation(
            id="test-bill-123",
            title="Test AI Regulation Bill",
            summary="A comprehensive bill regulating artificial intelligence",
            status="introduced",
            jurisdiction="federal",
            bill_number="HB-1234",
            introduced_date=datetime.now().date(),
            sponsors=["Rep. John Doe", "Sen. Jane Smith"],
            topics=["artificial intelligence", "technology", "regulation"],
            sentiment_score=0.7,
            enactment_probability=0.85,
            impact_score=8.5,
            full_text_url="https://example.com/bill-text"
        )

        db_session.add(legislation)
        await db_session.commit()
        await db_session.refresh(legislation)

        assert legislation.id == "test-bill-123"
        assert legislation.title == "Test AI Regulation Bill"
        assert legislation.status == "introduced"
        assert legislation.jurisdiction == "federal"
        assert legislation.sentiment_score == 0.7
        assert legislation.enactment_probability == 0.85
        assert legislation.impact_score == 8.5
        assert len(legislation.sponsors) == 2
        assert len(legislation.topics) == 3

    @pytest.mark.asyncio
    async def test_legislation_factory(self, db_session: AsyncSession):
        """Test Legislation factory."""
        legislation = LegislationFactory()
        db_session.add(legislation)
        await db_session.commit()

        assert legislation.id.startswith("bill-")
        assert legislation.title
        assert legislation.status in ["introduced", "passed", "failed"]
        assert legislation.sentiment_score >= -1
        assert legislation.sentiment_score <= 1


class TestPortfolio:
    """Test Portfolio model."""

    @pytest.mark.asyncio
    async def test_portfolio_creation(self, db_session: AsyncSession):
        """Test creating a portfolio."""
        portfolio = Portfolio(
            id="test-portfolio-456",
            name="Tech Growth Portfolio",
            description="Portfolio focused on technology companies",
            user_id=1,
            tickers=["AAPL", "MSFT", "GOOGL"],
        )

        db_session.add(portfolio)
        await db_session.commit()
        await db_session.refresh(portfolio)

        assert portfolio.id == "test-portfolio-456"
        assert portfolio.name == "Tech Growth Portfolio"
        assert portfolio.user_id == 1
        assert len(portfolio.tickers) == 3
        assert "AAPL" in portfolio.tickers

    @pytest.mark.asyncio
    async def test_portfolio_factory(self, db_session: AsyncSession):
        """Test Portfolio factory."""
        portfolio = PortfolioFactory()
        db_session.add(portfolio)
        await db_session.commit()

        assert portfolio.id.startswith("portfolio-")
        assert portfolio.name
        assert portfolio.tickers
        assert len(portfolio.tickers) >= 1


class TestAlertConfig:
    """Test AlertConfig model."""

    @pytest.mark.asyncio
    async def test_alert_config_creation(self, db_session: AsyncSession):
        """Test creating an alert configuration."""
        alert_config = AlertConfig(
            id="test-alert-config-789",
            name="AI Regulation Alerts",
            description="Alerts for AI-related legislation",
            keywords=["artificial intelligence", "machine learning", "AI regulation"],
            jurisdictions=["federal", "california"],
            severity_threshold="medium",
            notification_channels=["email", "webhook"],
            user_id=1,
            is_active=True
        )

        db_session.add(alert_config)
        await db_session.commit()
        await db_session.refresh(alert_config)

        assert alert_config.id == "test-alert-config-789"
        assert alert_config.name == "AI Regulation Alerts"
        assert alert_config.user_id == 1
        assert alert_config.is_active is True
        assert len(alert_config.keywords) == 3
        assert len(alert_config.jurisdictions) == 2
        assert "email" in alert_config.notification_channels

    @pytest.mark.asyncio
    async def test_alert_config_factory(self, db_session: AsyncSession):
        """Test AlertConfig factory."""
        alert_config = AlertConfigFactory()
        db_session.add(alert_config)
        await db_session.commit()

        assert alert_config.id.startswith("alert-config-")
        assert alert_config.name
        assert alert_config.keywords
        assert alert_config.jurisdictions


class TestAlert:
    """Test Alert model."""

    @pytest.mark.asyncio
    async def test_alert_creation(self, db_session: AsyncSession):
        """Test creating an alert."""
        alert = Alert(
            id="test-alert-101",
            title="New AI Regulation Bill Introduced",
            message="A new bill regulating artificial intelligence has been introduced in Congress",
            severity="high",
            category="legislation",
            user_id=1,
            legislation_id="bill-123",
            is_read=False
        )

        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)

        assert alert.id == "test-alert-101"
        assert alert.title == "New AI Regulation Bill Introduced"
        assert alert.severity == "high"
        assert alert.category == "legislation"
        assert alert.user_id == 1
        assert alert.is_read is False
        assert alert.legislation_id == "bill-123"

    @pytest.mark.asyncio
    async def test_alert_factory(self, db_session: AsyncSession):
        """Test Alert factory."""
        alert = AlertFactory()
        db_session.add(alert)
        await db_session.commit()

        assert alert.id.startswith("alert-")
        assert alert.title
        assert alert.message
        assert alert.severity in ["low", "medium", "high", "critical"]


class TestLegislationSentiment:
    """Test LegislationSentiment model."""

    @pytest.mark.asyncio
    async def test_sentiment_creation(self, db_session: AsyncSession):
        """Test creating legislation sentiment."""
        sentiment = LegislationSentiment(
            id=1,
            legislation_id="bill-123",
            positive_score=0.7,
            negative_score=0.2,
            neutral_score=0.1,
            confidence_score=0.85,
            analyzed_at=datetime.now()
        )

        db_session.add(sentiment)
        await db_session.commit()
        await db_session.refresh(sentiment)

        assert sentiment.id == 1
        assert sentiment.legislation_id == "bill-123"
        assert sentiment.positive_score == 0.7
        assert sentiment.negative_score == 0.2
        assert sentiment.neutral_score == 0.1
        assert sentiment.confidence_score == 0.85
        assert abs(sentiment.positive_score + sentiment.negative_score + sentiment.neutral_score - 1.0) < 0.01

    @pytest.mark.asyncio
    async def test_sentiment_factory(self, db_session: AsyncSession):
        """Test LegislationSentiment factory."""
        sentiment = LegislationSentimentFactory()
        db_session.add(sentiment)
        await db_session.commit()

        assert sentiment.id is not None
        assert sentiment.legislation_id.startswith("bill-")
        assert 0 <= sentiment.positive_score <= 1
        assert 0 <= sentiment.negative_score <= 1
        assert 0 <= sentiment.neutral_score <= 1
        assert abs(sentiment.positive_score + sentiment.negative_score + sentiment.neutral_score - 1.0) < 0.01


class TestMarketForecast:
    """Test MarketForecast model."""

    @pytest.mark.asyncio
    async def test_forecast_creation(self, db_session: AsyncSession):
        """Test creating market forecast."""
        forecast = MarketForecast(
            id=1,
            ticker="AAPL",
            forecast_date=datetime.now().date(),
            predicted_price=150.0,
            confidence_interval_low=140.0,
            confidence_interval_high=160.0,
            model_version="v2.1",
        )

        db_session.add(forecast)
        await db_session.commit()
        await db_session.refresh(forecast)

        assert forecast.id == 1
        assert forecast.ticker == "AAPL"
        assert forecast.predicted_price == 150.0
        assert forecast.confidence_interval_low == 140.0
        assert forecast.confidence_interval_high == 160.0
        assert forecast.model_version == "v2.1"

    @pytest.mark.asyncio
    async def test_forecast_factory(self, db_session: AsyncSession):
        """Test MarketForecast factory."""
        forecast = MarketForecastFactory()
        db_session.add(forecast)
        await db_session.commit()

        assert forecast.id is not None
        assert forecast.ticker in ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        assert forecast.predicted_price > 0
        assert forecast.confidence_interval_low < forecast.predicted_price
        assert forecast.confidence_interval_high > forecast.predicted_price


class TestOpportunity:
    """Test Opportunity model."""

    @pytest.mark.asyncio
    async def test_opportunity_creation(self, db_session: AsyncSession):
        """Test creating opportunity."""
        opportunity = Opportunity(
            id=1,
            title="AI Regulation Creates New Market Opportunities",
            description="The new AI regulation bill creates opportunities for compliance software",
            opportunity_type="market_expansion",
            impact_score=8.5,
            confidence_score=0.75,
            legislation_id="bill-123",
            tickers=["MSFT", "CRM"],
        )

        db_session.add(opportunity)
        await db_session.commit()
        await db_session.refresh(opportunity)

        assert opportunity.id == 1
        assert opportunity.title == "AI Regulation Creates New Market Opportunities"
        assert opportunity.opportunity_type == "market_expansion"
        assert opportunity.impact_score == 8.5
        assert opportunity.confidence_score == 0.75
        assert opportunity.legislation_id == "bill-123"
        assert len(opportunity.tickers) == 2

    @pytest.mark.asyncio
    async def test_opportunity_factory(self, db_session: AsyncSession):
        """Test Opportunity factory."""
        opportunity = OpportunityFactory()
        db_session.add(opportunity)
        await db_session.commit()

        assert opportunity.id is not None
        assert opportunity.title
        assert opportunity.opportunity_type in ["market_expansion", "regulatory_relief", "competitive_advantage"]
        assert opportunity.impact_score >= 0
        assert opportunity.confidence_score >= 0
        assert opportunity.confidence_score <= 1


class TestConflictScore:
    """Test ConflictScore model."""

    @pytest.mark.asyncio
    async def test_conflict_score_creation(self, db_session: AsyncSession):
        """Test creating conflict score."""
        conflict_score = ConflictScore(
            id=1,
            portfolio_id="portfolio-456",
            legislation_id="bill-123",
            conflict_score=0.8,
            risk_factors=["regulatory_risk", "compliance_cost", "market_impact"],
            calculated_at=datetime.now()
        )

        db_session.add(conflict_score)
        await db_session.commit()
        await db_session.refresh(conflict_score)

        assert conflict_score.id == 1
        assert conflict_score.portfolio_id == "portfolio-456"
        assert conflict_score.legislation_id == "bill-123"
        assert conflict_score.conflict_score == 0.8
        assert len(conflict_score.risk_factors) == 3
        assert "regulatory_risk" in conflict_score.risk_factors

    @pytest.mark.asyncio
    async def test_conflict_score_factory(self, db_session: AsyncSession):
        """Test ConflictScore factory."""
        conflict_score = ConflictScoreFactory()
        db_session.add(conflict_score)
        await db_session.commit()

        assert conflict_score.id is not None
        assert conflict_score.portfolio_id.startswith("portfolio-")
        assert conflict_score.legislation_id.startswith("bill-")
        assert 0 <= conflict_score.conflict_score <= 1
        assert conflict_score.risk_factors
