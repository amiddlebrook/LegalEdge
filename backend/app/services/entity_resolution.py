"""Entity resolution services."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.forecast import ForecastSignal
from app.models.insights import OpportunityRecommendation
from app.models.legislation import LegislativeBill
from app.models.portfolio import TradeDisclosure
from app.schemas.entity_resolution import (
    BillEntityLink,
    EntityEvidence,
    EntityResolutionSummary,
    ResolutionMetrics,
    TickerInsight,
)


async def build_entity_resolution_summary(session: AsyncSession | None = None) -> EntityResolutionSummary:
    """Return consolidated entity resolution coverage."""

    reference = datetime.now(timezone.utc)

    if session is None:
        logger.debug('Database session unavailable; returning stub entity resolution summary')
        return _stub_summary(reference)

    try:
        bill_result = await session.execute(select(LegislativeBill))
        bills = list(bill_result.scalars().all())
    except Exception as exc:  # pragma: no cover - defensive log
        logger.warning('Unable to fetch bills for entity resolution: %s', exc)
        return _stub_summary(reference)

    if not bills:
        logger.debug('No bill records present; returning stub entity resolution summary')
        return _stub_summary(reference)

    trades = await _safe_scalars(session, select(TradeDisclosure))
    forecasts = await _safe_scalars(session, select(ForecastSignal))
    opportunities = await _safe_scalars(session, select(OpportunityRecommendation))

    trade_index = defaultdict(list)
    for trade in trades:
        if trade.related_bill:
            trade_index[trade.related_bill].append(trade)

    sector_index = defaultdict(list)
    for forecast in forecasts:
        sector_index[forecast.sector].append(forecast)

    opportunity_index = defaultdict(list)
    for opportunity in opportunities:
        opportunity_index[opportunity.ticker].append(opportunity)

    bill_links: list[BillEntityLink] = []
    total_tickers = 0
    ticker_counter: Counter[str] = Counter()
    tracked_committees: set[str] = set()

    for bill in bills:
        committees = bill.committees or []
        sectors = bill.sectors or []
        tracked_committees.update(committees)

        evidence: list[EntityEvidence] = []
        tickers: set[str] = set()

        for trade in trade_index.get(bill.bill_id, []):
            tickers.add(trade.ticker)
            evidence.append(
                EntityEvidence(
                    source='trade',
                    ticker=trade.ticker,
                    description=f"{trade.member} {trade.transaction_type.lower()} disclosure",
                    weight=0.7,
                    metadata={
                        'member': trade.member,
                        'transaction_date': trade.transaction_date.isoformat(),
                        'chamber': trade.chamber,
                        'amount_range': trade.amount_range,
                    },
                )
            )

        for sector in sectors:
            for forecast in sector_index.get(sector, []):
                tickers.add(forecast.ticker)
                evidence.append(
                    EntityEvidence(
                        source='forecast',
                        ticker=forecast.ticker,
                        description=f"{forecast.ticker} forecast in {sector}",
                        weight=min(max(forecast.confidence, 0.0), 1.0),
                        metadata={
                            'expected_return_pct': forecast.expected_return_pct,
                            'confidence': forecast.confidence,
                            'horizon_days': forecast.horizon_days,
                        },
                    )
                )

        for ticker in list(tickers):
            for opportunity in opportunity_index.get(ticker, []):
                evidence.append(
                    EntityEvidence(
                        source='opportunity',
                        ticker=ticker,
                        description=f"Opportunity thesis: {opportunity.thesis[:60]}" + ('...' if len(opportunity.thesis) > 60 else ''),
                        weight=0.6,
                        metadata={
                            'expected_return_pct': opportunity.expected_return_pct,
                            'conviction': opportunity.conviction,
                            'horizon_days': opportunity.horizon_days,
                            'risk_rating': opportunity.risk_rating,
                        },
                    )
                )

        ordered_tickers = sorted(tickers)
        if ordered_tickers:
            total_tickers += len(ordered_tickers)
            for ticker in ordered_tickers:
                ticker_counter[ticker] += 1

        bill_links.append(
            BillEntityLink(
                bill_id=bill.bill_id,
                title=bill.title,
                jurisdiction=bill.jurisdiction,
                committees=committees,
                sectors=sectors,
                tickers=ordered_tickers,
                evidence=evidence,
                coverage_score=_compute_coverage_score(
                    committees=committees,
                    sectors=sectors,
                    tickers=ordered_tickers,
                    evidence=evidence,
                ),
            )
        )

    metrics = _build_metrics(
        bill_links=bill_links,
        total_bills=len(bills),
        total_tickers=total_tickers,
        unique_committees=tracked_committees,
    )

    top_entities = _summarize_top_entities(bill_links=bill_links, ticker_counter=ticker_counter)

    return EntityResolutionSummary(
        as_of=reference,
        metrics=metrics,
        bill_links=bill_links,
        top_entities=top_entities,
    )


def _compute_coverage_score(*, committees: list[str], sectors: list[str], tickers: list[str], evidence: list[EntityEvidence]) -> float:
    score = 0.0
    if committees:
        score += 0.2
    if sectors:
        score += min(len(sectors) * 0.1, 0.2)
    if tickers:
        score += min(len(tickers) * 0.25, 0.5)
    distinct_sources = {item.source for item in evidence}
    if distinct_sources:
        score += min(len(distinct_sources) * 0.1, 0.2)
    return round(min(score, 1.0), 2)


def _build_metrics(*, bill_links: list[BillEntityLink], total_bills: int, total_tickers: int, unique_committees: set[str]) -> ResolutionMetrics:
    bills_with_tickers = sum(1 for link in bill_links if link.tickers)
    coverage_ratio = bills_with_tickers / total_bills if total_bills else 0.0
    average_tickers = total_tickers / total_bills if total_bills else 0.0

    return ResolutionMetrics(
        total_bills=total_bills,
        bills_with_tickers=bills_with_tickers,
        coverage_ratio=round(coverage_ratio, 2),
        average_tickers_per_bill=round(average_tickers, 2),
        tracked_committees=len(unique_committees),
        orphan_bills=[link.bill_id for link in bill_links if not link.tickers],
    )


def _summarize_top_entities(*, bill_links: list[BillEntityLink], ticker_counter: Counter[str]) -> list[TickerInsight]:
    insights: list[TickerInsight] = []
    for ticker, count in ticker_counter.most_common(5):
        linked_bills = [link.bill_id for link in bill_links if ticker in link.tickers]
        sectors = sorted({sector for link in bill_links if ticker in link.tickers for sector in link.sectors})
        insights.append(
            TickerInsight(
                ticker=ticker,
                link_count=count,
                linked_bills=linked_bills,
                sectors=sectors,
            )
        )
    return insights


async def _safe_scalars(session: AsyncSession, statement):
    try:
        result = await session.execute(statement)
        return list(result.scalars().all())
    except Exception as exc:  # pragma: no cover - defensive log
        logger.warning('Entity resolution supplemental query failed: %s', exc)
        return []


def _stub_summary(reference: datetime) -> EntityResolutionSummary:
    links = [
        BillEntityLink(
            bill_id='LR-1000',
            title='AI Accountability and Transparency Act',
            jurisdiction='Federal',
            committees=['House Energy & Commerce'],
            sectors=['Technology', 'Financial Services'],
            tickers=['AIT', 'REGN'],
            evidence=[
                EntityEvidence(
                    source='trade',
                    ticker='AIT',
                    description='Sen. Jane Doe buy disclosure',
                    weight=0.7,
                    metadata={'member': 'Sen. Jane Doe', 'chamber': 'Senate'},
                ),
                EntityEvidence(
                    source='forecast',
                    ticker='REGN',
                    description='REGN forecast in Financial Services',
                    weight=0.68,
                    metadata={'expected_return_pct': 6.4},
                ),
            ],
            coverage_score=0.9,
        ),
        BillEntityLink(
            bill_id='TX-SB-88',
            title='Texas Grid Resilience Modernization',
            jurisdiction='State',
            committees=['Senate Business & Commerce'],
            sectors=['Energy', 'Utilities'],
            tickers=['GRID'],
            evidence=[
                EntityEvidence(
                    source='forecast',
                    ticker='GRID',
                    description='GRID forecast in Energy',
                    weight=0.63,
                )
            ],
            coverage_score=0.7,
        ),
    ]

    metrics = ResolutionMetrics(
        total_bills=4,
        bills_with_tickers=3,
        coverage_ratio=0.75,
        average_tickers_per_bill=0.75,
        tracked_committees=3,
        orphan_bills=['NYC-INT-2045'],
    )

    top_entities = [
        TickerInsight(ticker='AIT', link_count=1, linked_bills=['LR-1000'], sectors=['Technology']),
        TickerInsight(ticker='GRID', link_count=1, linked_bills=['TX-SB-88'], sectors=['Energy', 'Utilities']),
    ]

    return EntityResolutionSummary(
        as_of=reference,
        metrics=metrics,
        bill_links=links,
        top_entities=top_entities,
    )


__all__ = ['build_entity_resolution_summary']
