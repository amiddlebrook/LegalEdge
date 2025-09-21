"""Factory fixtures for generating test data."""

import factory
from factory import Faker, LazyAttribute, SubFactory
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    User, Legislation, Portfolio, Alert, AlertConfig,
    LegislationSentiment, MarketForecast, Opportunity,
    ConflictScore, CoverageMetric, DashboardWidget
)


class BaseFactory(factory.Factory):
    """Base factory with common functionality."""

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create instance asynchronously."""
        # This will be overridden in async tests
        pass


class UserFactory(BaseFactory):
    """Factory for User model."""

    class Meta:
        model = User

    id = factory.Sequence(lambda n: n)
    email = Faker("email")
    username = Faker("user_name")
    hashed_password = Faker("password")
    is_active = True
    is_superuser = False
    created_at = Faker("date_time_this_year")
    updated_at = Faker("date_time_this_year")


class LegislationFactory(BaseFactory):
    """Factory for Legislation model."""

    class Meta:
        model = Legislation

    id = factory.Sequence(lambda n: f"bill-{n}")
    title = Faker("sentence", nb_words=6)
    summary = Faker("text", max_nb_chars=200)
    status = Faker("random_element", elements=["introduced", "passed", "failed"])
    jurisdiction = Faker("random_element", elements=["federal", "california", "texas"])
    bill_number = Faker("bothify", text="??-####")
    introduced_date = Faker("date_this_year")
    sponsors = LazyAttribute(lambda obj: [Faker("name") for _ in range(2)])
    topics = LazyAttribute(lambda obj: [Faker("word") for _ in range(3)])
    sentiment_score = Faker("pyfloat", min_value=-1, max_value=1)
    enactment_probability = Faker("pyfloat", min_value=0, max_value=1)
    impact_score = Faker("pyfloat", min_value=0, max_value=10)
    full_text_url = Faker("url")
    created_at = Faker("date_time_this_year")
    updated_at = Faker("date_time_this_year")


class PortfolioFactory(BaseFactory):
    """Factory for Portfolio model."""

    class Meta:
        model = Portfolio

    id = factory.Sequence(lambda n: f"portfolio-{n}")
    name = Faker("company")
    description = Faker("text", max_nb_chars=100)
    user_id = factory.Sequence(lambda n: n)
    tickers = LazyAttribute(lambda obj: [Faker("random_element", elements=["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]) for _ in range(3)])
    created_at = Faker("date_time_this_year")
    updated_at = Faker("date_time_this_year")


class AlertConfigFactory(BaseFactory):
    """Factory for AlertConfig model."""

    class Meta:
        model = AlertConfig

    id = factory.Sequence(lambda n: f"alert-config-{n}")
    name = Faker("sentence", nb_words=3)
    description = Faker("text", max_nb_chars=100)
    keywords = LazyAttribute(lambda obj: [Faker("word") for _ in range(5)])
    jurisdictions = LazyAttribute(lambda obj: [Faker("random_element", elements=["federal", "california", "new_york"]) for _ in range(2)])
    severity_threshold = Faker("random_element", elements=["low", "medium", "high"])
    notification_channels = LazyAttribute(lambda obj: [Faker("random_element", elements=["email", "webhook", "sms"]) for _ in range(2)])
    user_id = factory.Sequence(lambda n: n)
    is_active = True
    created_at = Faker("date_time_this_year")
    updated_at = Faker("date_time_this_year")


class AlertFactory(BaseFactory):
    """Factory for Alert model."""

    class Meta:
        model = Alert

    id = factory.Sequence(lambda n: f"alert-{n}")
    title = Faker("sentence", nb_words=4)
    message = Faker("text", max_nb_chars=150)
    severity = Faker("random_element", elements=["low", "medium", "high", "critical"])
    category = Faker("random_element", elements=["legislation", "market", "portfolio", "system"])
    user_id = factory.Sequence(lambda n: n)
    legislation_id = factory.Sequence(lambda n: f"bill-{n}")
    is_read = False
    created_at = Faker("date_time_this_year")


class LegislationSentimentFactory(BaseFactory):
    """Factory for LegislationSentiment model."""

    class Meta:
        model = LegislationSentiment

    id = factory.Sequence(lambda n: n)
    legislation_id = factory.Sequence(lambda n: f"bill-{n}")
    positive_score = Faker("pyfloat", min_value=0, max_value=1)
    negative_score = Faker("pyfloat", min_value=0, max_value=1)
    neutral_score = Faker("pyfloat", min_value=0, max_value=1)
    confidence_score = Faker("pyfloat", min_value=0, max_value=1)
    analyzed_at = Faker("date_time_this_year")


class MarketForecastFactory(BaseFactory):
    """Factory for MarketForecast model."""

    class Meta:
        model = MarketForecast

    id = factory.Sequence(lambda n: n)
    ticker = Faker("random_element", elements=["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"])
    forecast_date = Faker("date_this_month")
    predicted_price = Faker("pyfloat", min_value=100, max_value=1000)
    confidence_interval_low = Faker("pyfloat", min_value=90, max_value=500)
    confidence_interval_high = Faker("pyfloat", min_value=500, max_value=1500)
    model_version = Faker("random_element", elements=["v1.0", "v2.0", "v3.0"])
    created_at = Faker("date_time_this_year")


class OpportunityFactory(BaseFactory):
    """Factory for Opportunity model."""

    class Meta:
        model = Opportunity

    id = factory.Sequence(lambda n: n)
    title = Faker("sentence", nb_words=4)
    description = Faker("text", max_nb_chars=200)
    opportunity_type = Faker("random_element", elements=["market_expansion", "regulatory_relief", "competitive_advantage"])
    impact_score = Faker("pyfloat", min_value=0, max_value=10)
    confidence_score = Faker("pyfloat", min_value=0, max_value=1)
    legislation_id = factory.Sequence(lambda n: f"bill-{n}")
    tickers = LazyAttribute(lambda obj: [Faker("random_element", elements=["AAPL", "MSFT", "GOOGL"]) for _ in range(2)])
    created_at = Faker("date_time_this_year")


class ConflictScoreFactory(BaseFactory):
    """Factory for ConflictScore model."""

    class Meta:
        model = ConflictScore

    id = factory.Sequence(lambda n: n)
    portfolio_id = factory.Sequence(lambda n: f"portfolio-{n}")
    legislation_id = factory.Sequence(lambda n: f"bill-{n}")
    conflict_score = Faker("pyfloat", min_value=0, max_value=1)
    risk_factors = LazyAttribute(lambda obj: [Faker("word") for _ in range(3)])
    calculated_at = Faker("date_time_this_year")
