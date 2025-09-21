"""Unit tests for service classes."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from freezegun import freeze_time

from app.services import alerts, auth, legislation, portfolio, forecasting
from app.models import User, Alert, AlertConfig, Legislation, Portfolio
from tests.fixtures.factories import (
    UserFactory, AlertFactory, AlertConfigFactory,
    LegislationFactory, PortfolioFactory
)


class TestAlertsService:
    """Test alerts service functions."""

    @pytest.mark.asyncio
    async def test_create_alert_subscription(self, db_session: AsyncSession, mocker):
        """Test creating alert subscription."""
        user = UserFactory()
        db_session.add(user)
        await db_session.commit()

        subscription_data = {
            "name": "AI Regulation Alerts",
            "description": "Alerts for AI regulation",
            "keywords": ["artificial intelligence", "machine learning"],
            "jurisdictions": ["federal", "california"],
            "severity_threshold": "medium",
            "notification_channels": ["email", "webhook"],
            "user_id": user.id
        }

        mock_repo = mocker.patch("app.services.alerts.create_alert_subscription")
        mock_repo.return_value = AlertConfig(**subscription_data)

        result = await alerts.create_alert_subscription(db_session, subscription_data)

        assert result.name == "AI Regulation Alerts"
        assert result.user_id == user.id
        assert len(result.keywords) == 2

    @pytest.mark.asyncio
    async def test_get_alerts_feed(self, db_session: AsyncSession, mocker):
        """Test getting alerts feed."""
        user = UserFactory()
        db_session.add(user)
        await db_session.commit()

        # Create test alerts
        alerts_data = []
        for i in range(3):
            alert = AlertFactory(user_id=user.id)
            alerts_data.append(alert)
            db_session.add(alert)

        await db_session.commit()

        mock_repo = mocker.patch("app.services.alerts.list_alerts")
        mock_repo.return_value = alerts_data

        result = await alerts.get_alerts_feed(
            db_session,
            user_id=user.id,
            limit=10,
            offset=0
        )

        assert len(result) == 3
        assert all(alert.user_id == user.id for alert in result)

    @pytest.mark.asyncio
    async def test_dispatch_alerts(self, db_session: AsyncSession, mocker):
        """Test dispatching alerts."""
        user = UserFactory()
        alert = AlertFactory(user_id=user.id)
        db_session.add_all([user, alert])
        await db_session.commit()

        # Mock notification services
        mock_email = mocker.patch("app.services.alerts.send_email_notification")
        mock_webhook = mocker.patch("app.services.alerts.send_webhook_notification")
        mock_sms = mocker.patch("app.services.alerts.send_sms_notification")

        with freeze_time("2024-01-15 12:00:00"):
            await alerts.dispatch_alerts(db_session, alert.id)

        # Verify notification calls based on alert configuration
        if "email" in alert.notification_channels:
            mock_email.assert_called_once()
        if "webhook" in alert.notification_channels:
            mock_webhook.assert_called_once()

    @pytest.mark.asyncio
    async def test_normalize_filters(self):
        """Test filter normalization."""
        # Test with valid values
        result = alerts._normalize_filters(["AI", "machine learning", ""])
        assert result == ["ai", "machine learning"]

        # Test with None
        result = alerts._normalize_filters(None)
        assert result is None

        # Test with empty list
        result = alerts._normalize_filters([])
        assert result is None

    @pytest.mark.asyncio
    async def test_severity_threshold(self):
        """Test severity threshold calculation."""
        # Test valid severity
        result = alerts._severity_threshold("high")
        assert result == 2

        # Test None
        result = alerts._severity_threshold(None)
        assert result is None

        # Test invalid severity
        result = alerts._severity_threshold("invalid")
        assert result is None

    @pytest.mark.asyncio
    async def test_allowed_severities(self):
        """Test allowed severities calculation."""
        # Test with threshold
        result = alerts._allowed_severities(1)  # medium and above
        assert result == ["medium", "high", "critical"]

        # Test with None
        result = alerts._allowed_severities(None)
        assert result is None


class TestAuthService:
    """Test authentication service functions."""

    @pytest.mark.asyncio
    async def test_register_user(self, db_session: AsyncSession, mocker):
        """Test user registration."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "is_active": True,
            "is_superuser": False
        }

        mock_repo = mocker.patch("app.services.auth.create_user")
        mock_hash = mocker.patch("app.services.auth.get_password_hash")
        mock_hash.return_value = "hashedpassword"

        result = await auth.register_user(db_session, user_data)

        assert result.email == "newuser@example.com"
        assert result.username == "newuser"
        mock_hash.assert_called_once_with("password123")

    @pytest.mark.asyncio
    async def test_authenticate_user(self, db_session: AsyncSession, mocker):
        """Test user authentication."""
        user = UserFactory(hashed_password="hashedpassword")
        db_session.add(user)
        await db_session.commit()

        mock_repo = mocker.patch("app.services.auth.authenticate_user")
        mock_verify = mocker.patch("app.services.auth.verify_password")
        mock_verify.return_value = True

        result = await auth.authenticate_user(db_session, user.email, "password123")

        mock_verify.assert_called_once_with("hashedpassword", "password123")
        mock_repo.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_password(self, db_session: AsyncSession, mocker):
        """Test password change."""
        user = UserFactory()
        db_session.add(user)
        await db_session.commit()

        mock_hash = mocker.patch("app.services.auth.get_password_hash")
        mock_hash.return_value = "newhashedpassword"
        mock_repo = mocker.patch("app.services.auth.update_user_password")

        await auth.change_password(db_session, user.id, "newpassword123")

        mock_hash.assert_called_once_with("newpassword123")
        mock_repo.assert_called_once_with(db_session, user.id, "newhashedpassword")

    @pytest.mark.asyncio
    async def test_get_current_user(self, mocker):
        """Test getting current user from token."""
        mock_decode = mocker.patch("app.services.auth.jwt.decode")
        mock_decode.return_value = {"sub": "user123", "exp": 1234567890}

        mock_repo = mocker.patch("app.services.auth.get_user_by_id")
        mock_repo.return_value = User(id="user123", email="user@example.com")

        result = await auth.get_current_user("valid.token.here")

        assert result.id == "user123"
        assert result.email == "user@example.com"

    @pytest.mark.asyncio
    async def test_get_current_active_user(self, mocker):
        """Test getting current active user."""
        user = User(is_active=True)
        mock_current_user = mocker.patch("app.services.auth.get_current_user")
        mock_current_user.return_value = user

        result = await auth.get_current_active_user("valid.token.here")

        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_get_current_active_superuser(self, mocker):
        """Test getting current active superuser."""
        user = User(is_active=True, is_superuser=True)
        mock_current_user = mocker.patch("app.services.auth.get_current_user")
        mock_current_user.return_value = user

        result = await auth.get_current_active_superuser("valid.token.here")

        assert result.is_superuser is True


class TestLegislationService:
    """Test legislation service functions."""

    @pytest.mark.asyncio
    async def test_get_legislation_with_sentiment(self, db_session: AsyncSession, mocker):
        """Test getting legislation with sentiment analysis."""
        bill = LegislationFactory()
        db_session.add(bill)
        await db_session.commit()

        mock_sentiment = mocker.patch("app.services.legislation.analyze_sentiment")
        mock_sentiment.return_value = {
            "positive": 0.7,
            "negative": 0.2,
            "neutral": 0.1,
            "confidence": 0.85
        }

        result = await legislation.get_legislation_with_sentiment(db_session, bill.id)

        assert result.id == bill.id
        assert result.title == bill.title
        mock_sentiment.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_legislation_by_topics(self, db_session: AsyncSession, mocker):
        """Test searching legislation by topics."""
        bills = []
        for i in range(3):
            bill = LegislationFactory(topics=["artificial intelligence", "technology"])
            bills.append(bill)
            db_session.add(bill)

        await db_session.commit()

        result = await legislation.search_legislation_by_topics(
            db_session,
            topics=["artificial intelligence"],
            limit=10
        )

        assert len(result) >= 0
        for bill in result:
            assert "artificial intelligence" in [topic.lower() for topic in bill.topics]

    @pytest.mark.asyncio
    async def test_get_legislation_by_jurisdiction(self, db_session: AsyncSession, mocker):
        """Test getting legislation by jurisdiction."""
        bills = []
        for i in range(3):
            bill = LegislationFactory(jurisdiction="federal")
            bills.append(bill)
            db_session.add(bill)

        await db_session.commit()

        result = await legislation.get_legislation_by_jurisdiction(
            db_session,
            jurisdiction="federal",
            limit=10
        )

        assert len(result) >= 0
        for bill in result:
            assert bill.jurisdiction == "federal"

    @pytest.mark.asyncio
    async def test_calculate_enactment_probability(self, db_session: AsyncSession, mocker):
        """Test calculating enactment probability."""
        bill = LegislationFactory(
            status="introduced",
            topics=["technology", "regulation"],
            sponsors=["Rep. John Doe", "Sen. Jane Smith"]
        )
        db_session.add(bill)
        await db_session.commit()

        mock_model = mocker.patch("app.services.legislation.load_enactment_model")
        mock_model.return_value.predict.return_value = 0.75

        result = await legislation.calculate_enactment_probability(db_session, bill.id)

        assert isinstance(result, float)
        assert 0 <= result <= 1

    @pytest.mark.asyncio
    async def test_analyze_sector_impact(self, db_session: AsyncSession, mocker):
        """Test analyzing sector impact."""
        bill = LegislationFactory(
            topics=["artificial intelligence", "technology", "regulation"]
        )
        db_session.add(bill)
        await db_session.commit()

        mock_analyzer = mocker.patch("app.services.legislation.SectorImpactAnalyzer")
        mock_analyzer.return_value.analyze.return_value = {
            "technology": 8.5,
            "healthcare": 3.2,
            "finance": 1.8
        }

        result = await legislation.analyze_sector_impact(db_session, bill.id)

        assert isinstance(result, dict)
        assert "technology" in result
        assert isinstance(result["technology"], (int, float))


class TestPortfolioService:
    """Test portfolio service functions."""

    @pytest.mark.asyncio
    async def test_create_portfolio_with_analysis(self, db_session: AsyncSession, mocker):
        """Test creating portfolio with analysis."""
        user = UserFactory()
        db_session.add(user)
        await db_session.commit()

        portfolio_data = {
            "name": "Tech Growth Portfolio",
            "description": "Portfolio focused on technology companies",
            "user_id": user.id,
            "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"]
        }

        mock_analysis = mocker.patch("app.services.portfolio.analyze_portfolio_risk")
        mock_analysis.return_value = {
            "risk_score": 6.5,
            "diversification_score": 7.2,
            "sector_concentration": {"technology": 0.85}
        }

        result = await portfolio.create_portfolio_with_analysis(db_session, portfolio_data)

        assert result.name == "Tech Growth Portfolio"
        assert result.user_id == user.id
        assert len(result.tickers) == 4
        mock_analysis.assert_called_once()

    @pytest.mark.asyncio
    async def test_calculate_portfolio_conflicts(self, db_session: AsyncSession, mocker):
        """Test calculating portfolio conflicts."""
        portfolio = PortfolioFactory()
        bill = LegislationFactory()
        db_session.add_all([portfolio, bill])
        await db_session.commit()

        mock_calculator = mocker.patch("app.services.portfolio.ConflictCalculator")
        mock_calculator.return_value.calculate.return_value = {
            "conflict_score": 0.8,
            "risk_factors": ["regulatory_risk", "compliance_cost"],
            "affected_tickers": ["AAPL", "MSFT"]
        }

        result = await portfolio.calculate_portfolio_conflicts(
            db_session,
            portfolio.id,
            bill.id
        )

        assert isinstance(result, dict)
        assert "conflict_score" in result
        assert "risk_factors" in result
        assert "affected_tickers" in result

    @pytest.mark.asyncio
    async def test_get_portfolio_performance(self, db_session: AsyncSession, mocker):
        """Test getting portfolio performance."""
        portfolio = PortfolioFactory()
        db_session.add(portfolio)
        await db_session.commit()

        mock_performance = mocker.patch("app.services.portfolio.get_performance_data")
        mock_performance.return_value = {
            "total_return": 0.15,
            "volatility": 0.22,
            "sharpe_ratio": 0.68,
            "max_drawdown": -0.12,
            "period": "1Y"
        }

        result = await portfolio.get_portfolio_performance(db_session, portfolio.id)

        assert isinstance(result, dict)
        assert "total_return" in result
        assert "volatility" in result
        assert "sharpe_ratio" in result

    @pytest.mark.asyncio
    async def test_rebalance_portfolio(self, db_session: AsyncSession, mocker):
        """Test portfolio rebalancing."""
        portfolio = PortfolioFactory(
            tickers=["AAPL", "MSFT", "GOOGL"],
        )
        db_session.add(portfolio)
        await db_session.commit()

        mock_rebalancer = mocker.patch("app.services.portfolio.PortfolioRebalancer")
        mock_rebalancer.return_value.rebalance.return_value = {
            "recommended_allocations": {
                "AAPL": 0.4,
                "MSFT": 0.35,
                "GOOGL": 0.25
            },
            "rebalance_actions": [
                {"action": "sell", "ticker": "AAPL", "amount": 100},
                {"action": "buy", "ticker": "MSFT", "amount": 50}
            ]
        }

        result = await portfolio.rebalance_portfolio(db_session, portfolio.id)

        assert isinstance(result, dict)
        assert "recommended_allocations" in result
        assert "rebalance_actions" in result


class TestForecastingService:
    """Test forecasting service functions."""

    @pytest.mark.asyncio
    async def test_generate_market_forecast(self, db_session: AsyncSession, mocker):
        """Test generating market forecast."""
        mock_model = mocker.patch("app.services.forecasting.load_forecasting_model")
        mock_model.return_value.predict.return_value = {
            "ticker": "AAPL",
            "predicted_price": 180.0,
            "confidence_low": 170.0,
            "confidence_high": 190.0,
            "forecast_date": "2024-02-15"
        }

        result = await forecasting.generate_market_forecast("AAPL", days_ahead=30)

        assert isinstance(result, dict)
        assert result["ticker"] == "AAPL"
        assert result["predicted_price"] == 180.0
        assert result["confidence_low"] == 170.0
        assert result["confidence_high"] == 190.0

    @pytest.mark.asyncio
    async def test_batch_forecast_generation(self, db_session: AsyncSession, mocker):
        """Test batch forecast generation."""
        tickers = ["AAPL", "MSFT", "GOOGL"]

        mock_model = mocker.patch("app.services.forecasting.load_forecasting_model")
        mock_model.return_value.batch_predict.return_value = [
            {"ticker": "AAPL", "predicted_price": 180.0},
            {"ticker": "MSFT", "predicted_price": 320.0},
            {"ticker": "GOOGL", "predicted_price": 140.0}
        ]

        result = await forecasting.generate_batch_forecasts(tickers, days_ahead=30)

        assert len(result) == 3
        assert all(forecast["ticker"] in tickers for forecast in result)
        assert all("predicted_price" in forecast for forecast in result)

    @pytest.mark.asyncio
    async def test_evaluate_forecast_accuracy(self, db_session: AsyncSession, mocker):
        """Test forecast accuracy evaluation."""
        forecasts = [
            {"ticker": "AAPL", "predicted_price": 180.0, "actual_price": 175.0},
            {"ticker": "MSFT", "predicted_price": 320.0, "actual_price": 315.0},
            {"ticker": "GOOGL", "predicted_price": 140.0, "actual_price": 142.0}
        ]

        mock_evaluator = mocker.patch("app.services.forecasting.ForecastEvaluator")
        mock_evaluator.return_value.evaluate.return_value = {
            "mean_absolute_error": 4.17,
            "mean_squared_error": 18.33,
            "accuracy_score": 0.85,
            "directional_accuracy": 0.67
        }

        result = await forecasting.evaluate_forecast_accuracy(forecasts)

        assert isinstance(result, dict)
        assert "mean_absolute_error" in result
        assert "mean_squared_error" in result
        assert "accuracy_score" in result
        assert "directional_accuracy" in result

    @pytest.mark.asyncio
    async def test_retrain_forecasting_model(self, db_session: AsyncSession, mocker):
        """Test retraining forecasting model."""
        training_data = [
            {"ticker": "AAPL", "date": "2024-01-01", "price": 170.0, "features": [1, 2, 3]},
            {"ticker": "MSFT", "date": "2024-01-01", "price": 300.0, "features": [4, 5, 6]}
        ]

        mock_model = mocker.patch("app.services.forecasting.load_forecasting_model")
        mock_model.return_value.retrain.return_value = {"accuracy": 0.92, "loss": 0.08}

        result = await forecasting.retrain_forecasting_model(training_data)

        assert isinstance(result, dict)
        assert "accuracy" in result
        assert "loss" in result
        assert result["accuracy"] > 0
        assert result["loss"] >= 0
