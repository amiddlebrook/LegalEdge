"""Development seeding utilities."""
from __future__ import annotations

import argparse
import asyncio
from datetime import date, datetime, timedelta, timezone
from typing import Iterable

from loguru import logger
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal, engine
from app.models import Base, ForecastSignal, LegislativeBill, TradeDisclosure


async def seed_sample_data(session: AsyncSession, *, reset: bool = False) -> None:
    """Populate the database with representative LegalEdge artifacts."""

    if reset:
        logger.info('Resetting existing sample data tables')
        for model in (LegislativeBill, ForecastSignal, TradeDisclosure):
            await session.execute(delete(model))

    existing_bills = await session.execute(select(LegislativeBill.bill_id))
    existing_bill_ids = {row[0] for row in existing_bills}

    upcoming_bills = list(_sample_bills())
    for bill in upcoming_bills:
        if bill.bill_id in existing_bill_ids:
            continue
        session.add(bill)

    existing_forecasts = await session.execute(select(ForecastSignal.ticker, ForecastSignal.sector))
    existing_forecast_keys = {(row[0], row[1]) for row in existing_forecasts}

    sector_forecasts = list(_sample_forecasts())
    for forecast in sector_forecasts:
        key = (forecast.ticker, forecast.sector)
        if key in existing_forecast_keys:
            continue
        session.add(forecast)

    existing_trades = await session.execute(select(TradeDisclosure.ticker, TradeDisclosure.transaction_date))
    existing_trade_keys = {(row[0], row[1]) for row in existing_trades}

    trade_disclosures = list(_sample_trades())
    for trade in trade_disclosures:
        key = (trade.ticker, trade.transaction_date)
        if key in existing_trade_keys:
            continue
        session.add(trade)

    await session.commit()
    logger.info(
        'Seed completed: %s bills, %s forecasts, %s trades',
        len(upcoming_bills),
        len(sector_forecasts),
        len(trade_disclosures),
    )


def _sample_bills() -> Iterable[LegislativeBill]:
    now = datetime.now(timezone.utc)
    base_next_action = date.today() + timedelta(days=7)
    for idx, (title, committees, sectors) in enumerate(
        [
            (
                'AI Accountability and Transparency Act',
                ['House Energy & Commerce'],
                ['Technology', 'Financial Services'],
            ),
            (
                'Responsible Algorithmic Governance Act',
                ['Senate Commerce, Science & Transportation'],
                ['Technology', 'Industrials'],
            ),
            (
                'Cyber Resilience for Critical Infrastructure Act',
                ['House Homeland Security'],
                ['Energy', 'Utilities'],
            ),
        ]
    ):
        yield LegislativeBill(
            bill_id=f'LR-{1000 + idx}',
            title=title,
            stage='Committee',
            jurisdiction='Federal',
            committees=committees,
            sectors=sectors,
            summary='Policy briefing placeholder generated for development seeding.',
            next_action_date=base_next_action + timedelta(days=idx * 3),
            sentiment_score=0.4 + idx * 0.05,
            probability_of_enactment=0.25 + idx * 0.08,
            last_updated=now,
        )


def _sample_forecasts() -> Iterable[ForecastSignal]:
    today = date.today()
    for sector, ticker, thesis, expected, confidence, catalysts in [
        (
            'Technology',
            'AIT',
            'Public sector AI procurement drives revenue acceleration.',
            7.5,
            0.72,
            ['Federal AI procurement bill', 'State algorithm audits'],
        ),
        (
            'Financial Services',
            'REGN',
            'Regtech compliance demand expands with transparency mandates.',
            6.2,
            0.68,
            ['SEC modernization roadmaps', 'Treasury disclosure pilot'],
        ),
        (
            'Energy',
            'GRID',
            'Infrastructure cybersecurity upgrades prompt new capital expenditure.',
            5.1,
            0.61,
            ['Critical infrastructure task force', 'Federal resilience grants'],
        ),
    ]:
        yield ForecastSignal(
            sector=sector,
            ticker=ticker,
            thesis=thesis,
            expected_return_pct=expected,
            confidence=confidence,
            catalysts=catalysts,
            horizon_days=45,
            generated_on=today,
        )


def _sample_trades() -> Iterable[TradeDisclosure]:
    base_time = datetime.now(timezone.utc) - timedelta(days=2)
    for idx, (member, chamber, ticker, txn_type, related_bill) in enumerate(
        [
            ('Sen. Jane Doe', 'Senate', 'AIT', 'BUY', 'LR-1000'),
            ('Rep. Alex Smith', 'House', 'REGN', 'BUY', 'LR-1001'),
            ('Sen. Malik Johnson', 'Senate', 'GRID', 'SELL', None),
        ]
    ):
        yield TradeDisclosure(
            member=member,
            chamber=chamber,
            ticker=ticker,
            transaction_type=txn_type,
            transaction_date=base_time - timedelta(hours=idx * 6),
            amount_range='$15k-$50k',
            related_bill=related_bill,
        )


async def _ensure_schema() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Seed LegalEdge development data')
    parser.add_argument('--reset', action='store_true', help='Reset tables before inserting data')
    return parser.parse_args()


async def _run_cli(reset: bool) -> None:
    await _ensure_schema()
    async with SessionLocal() as session:
        await seed_sample_data(session, reset=reset)


def main() -> None:
    args = _parse_args()
    asyncio.run(_run_cli(reset=args.reset))


if __name__ == '__main__':
    main()