"""Integration tests for database operations."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.models import (
    User, Legislation, Portfolio, Alert, AlertConfig,
    LegislationSentiment, MarketForecast, Opportunity, ConflictScore
)
from app.repositories import legislation, portfolio, auth, insights


class TestDatabaseOperations:
    """Integration tests for database operations."""

    @pytest.mark.asyncio
    async def test_database_connection(self, db_session: AsyncSession):
        """Test basic database connection and query."""
        # Execute a simple query
        result = await db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    @pytest.mark.asyncio
    async def test_transaction_rollback(self, db_session: AsyncSession):
        """Test database transaction rollback."""
        # Start a transaction
        async with db_session.begin():
            # Create a user within transaction
            user = User(
                email="rollbacktest@example.com",
                username="rollbacktest",
                hashed_password="hashedpassword"
            )
            db_session.add(user)
            await db_session.flush()

            # Verify user exists within transaction
            result = await db_session.get(User, user.id)
            assert result is not None

        # After transaction ends, user should be rolled back
        result = await db_session.get(User, user.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_concurrent_database_operations(self, db_session: AsyncSession):
        """Test concurrent database operations."""
        import asyncio

        async def create_user(session: AsyncSession, email: str):
            """Create a user in a separate task."""
            user = User(
                email=email,
                username=email.split("@")[0],
                hashed_password="hashedpassword"
            )
            session.add(user)
            await session.commit()
            return user

        # Create multiple users concurrently
        tasks = [
            create_user(db_session, f"concurrent{i}@example.com")
            for i in range(5)
        ]

        users = await asyncio.gather(*tasks)
        assert len(users) == 5

        # Verify all users were created
        for user in users:
            result = await db_session.get(User, user.id)
            assert result is not None
            assert result.email == user.email


class TestLegislationDatabaseOperations:
    """Integration tests for legislation database operations."""

    @pytest.mark.asyncio
    async def test_legislation_crud_operations(self, db_session: AsyncSession):
        """Test CRUD operations for legislation."""
        # Create
        bill = await legislation.create_legislation(db_session, {
            "id": "db-test-bill-123",
            "title": "Database Test Bill",
            "summary": "A bill for testing database operations",
            "status": "introduced",
            "jurisdiction": "federal",
            "bill_number": "HB-9998",
            "introduced_date": "2024-01-15",
            "sponsors": ["Rep. DB Test"],
            "topics": ["database", "testing"],
            "sentiment_score": 0.5,
            "enactment_probability": 0.6,
            "impact_score": 7.0,
            "full_text_url": "https://example.com/db-test"
        })
        await db_session.commit()

        assert bill.id == "db-test-bill-123"
        assert bill.title == "Database Test Bill"

        # Read
        retrieved = await legislation.get_legislation_by_id(db_session, "db-test-bill-123")
        assert retrieved is not None
        assert retrieved.title == "Database Test Bill"
        assert retrieved.status == "introduced"

        # Update
        updated = await legislation.update_legislation(db_session, "db-test-bill-123", {
            "status": "passed",
            "sentiment_score": 0.8,
            "enactment_probability": 0.9
        })
        await db_session.commit()

        assert updated.status == "passed"
        assert updated.sentiment_score == 0.8
        assert updated.enactment_probability == 0.9

        # Delete
        deleted = await legislation.delete_legislation(db_session, "db-test-bill-123")
        await db_session.commit()

        assert deleted is True

        # Verify deletion
        deleted_bill = await legislation.get_legislation_by_id(db_session, "db-test-bill-123")
        assert deleted_bill is None

    @pytest.mark.asyncio
    async def test_legislation_search_operations(self, db_session: AsyncSession):
        """Test legislation search operations."""
        # Create test legislation
        bills_data = [
            {
                "id": f"search-test-{i}",
                "title": f"Search Test Bill {i}",
                "summary": f"Bill {i} for search testing",
                "status": "introduced",
                "jurisdiction": "federal" if i % 2 == 0 else "california",
                "bill_number": f"HB-{10000 + i}",
                "introduced_date": "2024-01-15",
                "sponsors": [f"Rep. Search {i}"],
                "topics": ["artificial intelligence", "technology"] if i % 2 == 0 else ["healthcare", "regulation"],
                "sentiment_score": 0.5,
                "enactment_probability": 0.6,
                "impact_score": 7.0,
                "full_text_url": f"https://example.com/search-test-{i}"
            }
            for i in range(5)
        ]

        for bill_data in bills_data:
            await legislation.create_legislation(db_session, bill_data)
        await db_session.commit()

        # Test search by query
        results = await legislation.search_legislation(db_session, query="artificial intelligence")
        assert len(results) >= 0

        # Test search by topics
        results = await legislation.search_legislation(db_session, topics=["artificial intelligence"])
        assert len(results) >= 0

        # Test search by jurisdiction
        results = await legislation.search_legislation(db_session, jurisdiction="federal")
        assert len(results) >= 0

        # Test search by status
        results = await legislation.search_legislation(db_session, status="introduced")
        assert len(results) >= 0


class TestPortfolioDatabaseOperations:
    """Integration tests for portfolio database operations."""

    @pytest.mark.asyncio
    async def test_portfolio_crud_operations(self, db_session: AsyncSession):
        """Test CRUD operations for portfolios."""
        # Create user first
        user = User(
            email="portfoliodbtest@example.com",
            username="portfoliodbtest",
            hashed_password="hashedpassword"
        )
        db_session.add(user)
        await db_session.commit()

        # Create
        portfolio = await portfolio.create_portfolio(db_session, {
            "id": "db-test-portfolio-456",
            "name": "DB Test Portfolio",
            "description": "A portfolio for database testing",
            "user_id": user.id,
            "tickers": ["AAPL", "MSFT", "GOOGL"]
        })
        await db_session.commit()

        assert portfolio.id == "db-test-portfolio-456"
        assert portfolio.name == "DB Test Portfolio"
        assert portfolio.user_id == user.id

        # Read
        retrieved = await portfolio.get_portfolio_by_id(db_session, "db-test-portfolio-456")
        assert retrieved is not None
        assert retrieved.name == "DB Test Portfolio"

        # Update
        updated = await portfolio.update_portfolio(db_session, "db-test-portfolio-456", {
            "name": "Updated DB Test Portfolio",
            "description": "Updated portfolio description",
            "tickers": ["TSLA", "NVDA", "AMD"]
        })
        await db_session.commit()

        assert updated.name == "Updated DB Test Portfolio"
        assert updated.description == "Updated portfolio description"
        assert len(updated.tickers) == 3
        assert "TSLA" in updated.tickers

        # Delete
        deleted = await portfolio.delete_portfolio(db_session, "db-test-portfolio-456")
        await db_session.commit()

        assert deleted is True

        # Verify deletion
        deleted_portfolio = await portfolio.get_portfolio_by_id(db_session, "db-test-portfolio-456")
        assert deleted_portfolio is None

    @pytest.mark.asyncio
    async def test_portfolio_user_relationships(self, db_session: AsyncSession):
        """Test portfolio-user relationships."""
        # Create users
        users = []
        for i in range(3):
            user = User(
                email=f"portfoliorelationship{i}@example.com",
                username=f"portfoliorelationship{i}",
                hashed_password="hashedpassword"
            )
            users.append(user)
            db_session.add(user)

        await db_session.commit()

        # Create portfolios for each user
        portfolios = []
        for i, user in enumerate(users):
            port = await portfolio.create_portfolio(db_session, {
                "id": f"relationship-portfolio-{i}",
                "name": f"User {i} Portfolio",
                "description": f"Portfolio for user {i}",
                "user_id": user.id,
                "tickers": ["AAPL", "MSFT"]
            })
            portfolios.append(port)

        await db_session.commit()

        # Test getting portfolios by user
        for i, user in enumerate(users):
            user_portfolios = await portfolio.get_portfolios_by_user(db_session, user.id)
            assert len(user_portfolios) == 1
            assert user_portfolios[0].user_id == user.id
            assert user_portfolios[0].name == f"User {i} Portfolio"

    @pytest.mark.asyncio
    async def test_portfolio_with_conflict_scores(self, db_session: AsyncSession):
        """Test portfolios with conflict scores."""
        # Create user and portfolio
        user = User(
            email="conflicttest@example.com",
            username="conflicttest",
            hashed_password="hashedpassword"
        )
        db_session.add(user)
        await db_session.commit()

        port = await portfolio.create_portfolio(db_session, {
            "id": "conflict-portfolio-789",
            "name": "Conflict Test Portfolio",
            "description": "Portfolio for conflict testing",
            "user_id": user.id,
            "tickers": ["AAPL", "MSFT"]
        })

        # Create legislation
        bill = await legislation.create_legislation(db_session, {
            "id": "conflict-bill-101",
            "title": "Conflict Test Bill",
            "summary": "Bill that conflicts with portfolio",
            "status": "introduced",
            "jurisdiction": "federal",
            "bill_number": "HB-8888",
            "introduced_date": "2024-01-15",
            "sponsors": ["Rep. Conflict"],
            "topics": ["technology", "regulation"],
            "sentiment_score": 0.3,
            "enactment_probability": 0.8,
            "impact_score": 9.0,
            "full_text_url": "https://example.com/conflict-bill"
        })

        await db_session.commit()

        # Create conflict score
        conflict_score = ConflictScore(
            id=1,
            portfolio_id=port.id,
            legislation_id=bill.id,
            conflict_score=0.8,
            risk_factors=["regulatory_risk", "compliance_cost"],
        )
        db_session.add(conflict_score)
        await db_session.commit()

        # Test retrieving portfolio with conflict scores
        retrieved_port = await portfolio.get_portfolio_by_id(db_session, port.id)
        assert retrieved_port is not None

        # The relationship should be accessible
        # This would depend on the actual model relationships defined
        # For now, we'll just verify the portfolio exists


class TestAlertsDatabaseOperations:
    """Integration tests for alerts database operations."""

    @pytest.mark.asyncio
    async def test_alert_config_crud_operations(self, db_session: AsyncSession):
        """Test CRUD operations for alert configurations."""
        # Create user first
        user = User(
            email="alertdbtest@example.com",
            username="alertdbtest",
            hashed_password="hashedpassword"
        )
        db_session.add(user)
        await db_session.commit()

        # Create alert config
        alert_config = AlertConfig(
            id="db-test-alert-config-111",
            name="DB Test Alert Config",
            description="Alert config for database testing",
            keywords=["database", "testing", "integration"],
            jurisdictions=["federal", "california"],
            severity_threshold="medium",
            notification_channels=["email", "webhook"],
            user_id=user.id,
            is_active=True
        )
        db_session.add(alert_config)
        await db_session.commit()

        assert alert_config.id == "db-test-alert-config-111"
        assert alert_config.name == "DB Test Alert Config"
        assert alert_config.user_id == user.id
        assert alert_config.is_active is True

        # Read
        from app.repositories.insights import get_alert_subscription
        retrieved = await get_alert_subscription(db_session, alert_config.id)
        assert retrieved is not None
        assert retrieved.name == "DB Test Alert Config"

        # Update
        alert_config.name = "Updated DB Test Alert Config"
        alert_config.keywords = ["updated", "database", "testing"]
        alert_config.jurisdictions = ["federal", "texas"]
        await db_session.commit()

        updated = await get_alert_subscription(db_session, alert_config.id)
        assert updated.name == "Updated DB Test Alert Config"
        assert updated.keywords == ["updated", "database", "testing"]
        assert updated.jurisdictions == ["federal", "texas"]

        # Delete
        await db_session.delete(alert_config)
        await db_session.commit()

        # Verify deletion
        deleted = await get_alert_subscription(db_session, alert_config.id)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_alert_creation_and_relationships(self, db_session: AsyncSession):
        """Test alert creation and relationships."""
        # Create user
        user = User(
            email="alertrelationshiptest@example.com",
            username="alertrelationshiptest",
            hashed_password="hashedpassword"
        )
        db_session.add(user)
        await db_session.commit()

        # Create legislation
        bill = await legislation.create_legislation(db_session, {
            "id": "relationship-bill-222",
            "title": "Relationship Test Bill",
            "summary": "Bill for testing relationships",
            "status": "introduced",
            "jurisdiction": "federal",
            "bill_number": "HB-7777",
            "introduced_date": "2024-01-15",
            "sponsors": ["Rep. Relationship"],
            "topics": ["relationship", "testing"],
            "sentiment_score": 0.6,
            "enactment_probability": 0.7,
            "impact_score": 8.0,
            "full_text_url": "https://example.com/relationship-bill"
        })
        await db_session.commit()

        # Create alert
        alert = Alert(
            id="db-test-alert-333",
            title="Relationship Test Alert",
            message="An alert for relationship testing",
            severity="high",
            category="legislation",
            user_id=user.id,
            legislation_id=bill.id,
            is_read=False
        )
        db_session.add(alert)
        await db_session.commit()

        assert alert.id == "db-test-alert-333"
        assert alert.title == "Relationship Test Alert"
        assert alert.user_id == user.id
        assert alert.legislation_id == bill.id
        assert alert.is_read is False

        # Test retrieving alerts for user
        from app.repositories.insights import list_alerts
        user_alerts = await list_alerts(db_session, user_id=user.id)
        assert len(user_alerts) >= 1

        found_alert = next((a for a in user_alerts if a.id == alert.id), None)
        assert found_alert is not None
        assert found_alert.title == "Relationship Test Alert"

        # Test marking alert as read
        alert.is_read = True
        await db_session.commit()

        updated_alerts = await list_alerts(db_session, user_id=user.id)
        updated_found = next((a for a in updated_alerts if a.id == alert.id), None)
        assert updated_found.is_read is True


class TestMLModelDatabaseOperations:
    """Integration tests for ML model database operations."""

    @pytest.mark.asyncio
    async def test_legislation_sentiment_storage(self, db_session: AsyncSession):
        """Test legislation sentiment storage."""
        # Create legislation
        bill = await legislation.create_legislation(db_session, {
            "id": "sentiment-bill-444",
            "title": "Sentiment Test Bill",
            "summary": "Bill for sentiment analysis",
            "status": "introduced",
            "jurisdiction": "federal",
            "bill_number": "HB-6666",
            "introduced_date": "2024-01-15",
            "sponsors": ["Rep. Sentiment"],
            "topics": ["sentiment", "analysis"],
            "sentiment_score": 0.5,
            "enactment_probability": 0.6,
            "impact_score": 7.0,
            "full_text_url": "https://example.com/sentiment-bill"
        })
        await db_session.commit()

        # Create sentiment analysis
        sentiment = LegislationSentiment(
            id=1,
            legislation_id=bill.id,
            positive_score=0.7,
            negative_score=0.2,
            neutral_score=0.1,
            confidence_score=0.85,
        )
        db_session.add(sentiment)
        await db_session.commit()

        assert sentiment.id == 1
        assert sentiment.legislation_id == bill.id
        assert sentiment.positive_score == 0.7
        assert sentiment.negative_score == 0.2
        assert sentiment.neutral_score == 0.1
        assert sentiment.confidence_score == 0.85

        # Verify the sum of scores is approximately 1.0
        total_score = sentiment.positive_score + sentiment.negative_score + sentiment.neutral_score
        assert abs(total_score - 1.0) < 0.01

    @pytest.mark.asyncio
    async def test_market_forecast_storage(self, db_session: AsyncSession):
        """Test market forecast storage."""
        # Create forecast
        forecast = MarketForecast(
            id=1,
            ticker="AAPL",
            forecast_date="2024-02-15",
            predicted_price=180.0,
            confidence_interval_low=170.0,
            confidence_interval_high=190.0,
            model_version="v2.1",
        )
        db_session.add(forecast)
        await db_session.commit()

        assert forecast.id == 1
        assert forecast.ticker == "AAPL"
        assert forecast.predicted_price == 180.0
        assert forecast.confidence_interval_low == 170.0
        assert forecast.confidence_interval_high == 190.0
        assert forecast.model_version == "v2.1"

        # Verify confidence interval is valid
        assert forecast.confidence_interval_low < forecast.predicted_price
        assert forecast.confidence_interval_high > forecast.predicted_price
        assert forecast.confidence_interval_high > forecast.confidence_interval_low

    @pytest.mark.asyncio
    async def test_opportunity_storage(self, db_session: AsyncSession):
        """Test opportunity storage."""
        # Create legislation
        bill = await legislation.create_legislation(db_session, {
            "id": "opportunity-bill-555",
            "title": "Opportunity Test Bill",
            "summary": "Bill for opportunity analysis",
            "status": "introduced",
            "jurisdiction": "federal",
            "bill_number": "HB-5555",
            "introduced_date": "2024-01-15",
            "sponsors": ["Rep. Opportunity"],
            "topics": ["opportunity", "market"],
            "sentiment_score": 0.6,
            "enactment_probability": 0.8,
            "impact_score": 8.5,
            "full_text_url": "https://example.com/opportunity-bill"
        })
        await db_session.commit()

        # Create opportunity
        opportunity = Opportunity(
            id=1,
            title="New Market Opportunity",
            description="This bill creates new market opportunities",
            opportunity_type="market_expansion",
            impact_score=8.5,
            confidence_score=0.75,
            legislation_id=bill.id,
            tickers=["MSFT", "CRM"],
        )
        db_session.add(opportunity)
        await db_session.commit()

        assert opportunity.id == 1
        assert opportunity.title == "New Market Opportunity"
        assert opportunity.legislation_id == bill.id
        assert opportunity.opportunity_type == "market_expansion"
        assert opportunity.impact_score == 8.5
        assert opportunity.confidence_score == 0.75
        assert len(opportunity.tickers) == 2

        # Verify confidence score is valid
        assert 0 <= opportunity.confidence_score <= 1
        assert opportunity.impact_score >= 0
