#!/usr/bin/env python3
"""
Database seeding script for LegalEdge development environment.

This script populates the database with sample legislative bills, forecast signals,
and other essential data for development and testing purposes.
"""

import asyncio
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.legislation import LegislativeBill
from app.models.forecasts import ForecastSignal
from app.models.portfolios import Portfolio, PortfolioBill, PortfolioSignal
from app.models.alerts import Alert, AlertSubscription
from app.models.auth import User


async def seed_legislative_bills(session: Session) -> None:
    """Seed legislative bills with sample data."""
    bills_data = [
        {
            "bill_id": "HR-1234",
            "title": "Climate Action and Investment Act of 2024",
            "stage": "Committee",
            "jurisdiction": "Federal",
            "committees": ["Energy and Commerce", "Financial Services"],
            "sectors": ["Energy", "Financial Services", "Technology"],
            "summary": "Comprehensive legislation to accelerate clean energy transition and provide investment incentives for sustainable technologies.",
            "next_action_date": datetime.now() + timedelta(days=45),
            "sentiment_score": 0.8,
            "probability_of_enactment": 0.75,
        },
        {
            "bill_id": "S-567",
            "title": "Digital Asset Regulation Framework",
            "stage": "Floor Vote",
            "jurisdiction": "Federal",
            "committees": ["Banking, Housing, and Urban Affairs"],
            "sectors": ["Financial Services", "Technology"],
            "summary": "Establishes regulatory framework for digital assets, stablecoins, and cryptocurrency exchanges.",
            "next_action_date": datetime.now() + timedelta(days=15),
            "sentiment_score": 0.6,
            "probability_of_enactment": 0.65,
        },
        {
            "bill_id": "CA-AB-890",
            "title": "California Privacy Enhancement Act",
            "stage": "Enacted",
            "jurisdiction": "California",
            "committees": ["Judiciary", "Business and Professions"],
            "sectors": ["Technology", "Healthcare"],
            "summary": "Expands consumer privacy rights and imposes stricter data handling requirements on businesses.",
            "next_action_date": None,
            "sentiment_score": 0.9,
            "probability_of_enactment": 1.0,
        },
        {
            "bill_id": "TX-SB-456",
            "title": "Texas Energy Independence Act",
            "stage": "Committee",
            "jurisdiction": "Texas",
            "committees": ["Natural Resources and Economic Development"],
            "sectors": ["Energy", "Utilities"],
            "summary": "Promotes energy independence through incentives for oil and gas production and reduced renewable mandates.",
            "next_action_date": datetime.now() + timedelta(days=60),
            "sentiment_score": -0.3,
            "probability_of_enactment": 0.45,
        },
        {
            "bill_id": "HR-789",
            "title": "Healthcare Accessibility and Innovation Act",
            "stage": "Markup",
            "jurisdiction": "Federal",
            "committees": ["Energy and Commerce", "Ways and Means"],
            "sectors": ["Healthcare", "Technology"],
            "summary": "Expands telehealth services and promotes innovation in healthcare delivery through regulatory reforms.",
            "next_action_date": datetime.now() + timedelta(days=30),
            "sentiment_score": 0.7,
            "probability_of_enactment": 0.80,
        },
    ]

    for bill_data in bills_data:
        bill = LegislativeBill(**bill_data)
        session.add(bill)

    await session.commit()
    print(f"✅ Seeded {len(bills_data)} legislative bills")


async def seed_forecast_signals(session: Session) -> None:
    """Seed forecast signals with sample market predictions."""
    signals_data = [
        {
            "sector": "Technology",
            "ticker": "AAPL",
            "thesis": "Strong iPhone demand and services growth driven by regulatory scrutiny on competitors",
            "expected_return_pct": 15.5,
            "confidence": 0.85,
            "catalysts": ["New product launches", "Services revenue growth", "Regulatory environment"],
            "horizon_days": 90,
            "generated_on": datetime.now().date(),
        },
        {
            "sector": "Energy",
            "ticker": "TSLA",
            "thesis": "EV market leadership and autonomous driving technology advancement",
            "expected_return_pct": 25.0,
            "confidence": 0.75,
            "catalysts": ["Model 3 production ramp", "Autopilot regulatory approval", "Battery cost reductions"],
            "horizon_days": 180,
            "generated_on": datetime.now().date(),
        },
        {
            "sector": "Healthcare",
            "ticker": "PFE",
            "thesis": "Patent cliff concerns but strong vaccine pipeline and acquisition synergies",
            "expected_return_pct": -5.2,
            "confidence": 0.70,
            "catalysts": ["COVID vaccine demand", "New drug approvals", "Patent expirations"],
            "horizon_days": 60,
            "generated_on": datetime.now().date(),
        },
        {
            "sector": "Financial Services",
            "ticker": "JPM",
            "thesis": "Interest rate environment and regulatory changes impacting lending margins",
            "expected_return_pct": 8.3,
            "confidence": 0.80,
            "catalysts": ["Fed rate decisions", "Regulatory reforms", "Economic growth"],
            "horizon_days": 120,
            "generated_on": datetime.now().date(),
        },
        {
            "sector": "Technology",
            "ticker": "MSFT",
            "thesis": "Cloud growth acceleration and AI integration across product portfolio",
            "expected_return_pct": 18.7,
            "confidence": 0.90,
            "catalysts": ["Azure market share gains", "AI product launches", "Enterprise adoption"],
            "horizon_days": 90,
            "generated_on": datetime.now().date(),
        },
    ]

    for signal_data in signals_data:
        signal = ForecastSignal(**signal_data)
        session.add(signal)

    await session.commit()
    print(f"✅ Seeded {len(signals_data)} forecast signals")


async def seed_portfolios(session: Session) -> None:
    """Seed sample portfolios for demonstration."""
    # Create sample users first
    users_data = [
        {"username": "investor_jane", "email": "jane@example.com", "full_name": "Jane Smith"},
        {"username": "portfolio_manager_mike", "email": "mike@fund.com", "full_name": "Mike Johnson"},
    ]

    users = []
    for user_data in users_data:
        user = User(**user_data)
        session.add(user)
        users.append(user)

    await session.commit()

    # Create sample portfolios
    portfolios_data = [
        {
            "name": "Growth Tech Portfolio",
            "description": "High-growth technology companies with policy exposure",
            "user_id": users[0].id,
        },
        {
            "name": "Conservative Value Portfolio",
            "description": "Stable companies with defensive characteristics",
            "user_id": users[1].id,
        },
    ]

    portfolios = []
    for portfolio_data in portfolios_data:
        portfolio = Portfolio(**portfolio_data)
        session.add(portfolio)
        portfolios.append(portfolio)

    await session.commit()

    # Link bills and signals to portfolios
    bills = session.query(LegislativeBill).all()
    signals = session.query(ForecastSignal).all()

    for i, portfolio in enumerate(portfolios):
        # Link some bills to each portfolio
        for j in range(min(2, len(bills))):
            portfolio_bill = PortfolioBill(
                portfolio_id=portfolio.id,
                bill_id=bills[j].id,
                weight=0.1 + (j * 0.05)
            )
            session.add(portfolio_bill)

        # Link some signals to each portfolio
        for j in range(min(2, len(signals))):
            portfolio_signal = PortfolioSignal(
                portfolio_id=portfolio.id,
                signal_id=signals[j].id,
                weight=0.15 + (j * 0.05)
            )
            session.add(portfolio_signal)

    await session.commit()
    print(f"✅ Seeded {len(portfolios_data)} portfolios with associated bills and signals")


async def seed_alerts_and_subscriptions(session: Session) -> None:
    """Seed sample alerts and subscriptions."""
    users = session.query(User).all()

    # Create alert subscriptions
    subscriptions_data = [
        {
            "user_id": users[0].id,
            "alert_type": "legislation",
            "jurisdiction": "Federal",
            "sectors": ["Technology", "Healthcare"],
            "frequency": "immediate",
        },
        {
            "user_id": users[1].id,
            "alert_type": "forecast",
            "confidence_threshold": 0.8,
            "frequency": "daily",
        },
    ]

    for subscription_data in subscriptions_data:
        subscription = AlertSubscription(**subscription_data)
        session.add(subscription)

    await session.commit()

    # Create sample alerts
    alerts_data = [
        {
            "title": "New Climate Legislation Introduced",
            "message": "HR-1234 Climate Action and Investment Act has been introduced with strong bipartisan support",
            "alert_type": "legislation",
            "severity": "medium",
            "user_id": users[0].id,
        },
        {
            "title": "High Confidence Tech Forecast",
            "message": "New forecast signal for AAPL shows 15.5% expected return with 85% confidence",
            "alert_type": "forecast",
            "severity": "high",
            "user_id": users[1].id,
        },
    ]

    for alert_data in alerts_data:
        alert = Alert(**alert_data)
        session.add(alert)

    await session.commit()
    print(f"✅ Seeded {len(subscriptions_data)} alert subscriptions and {len(alerts_data)} alerts")


async def main() -> None:
    """Run all seeding operations."""
    async with SessionLocal() as session:
        print("🌱 Starting database seeding...")

        await seed_legislative_bills(session)
        await seed_forecast_signals(session)
        await seed_portfolios(session)
        await seed_alerts_and_subscriptions(session)

        print("✅ Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
