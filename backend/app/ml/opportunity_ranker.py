from __future__ import annotations

"""Opportunity ranking utilities combining policy and conflict signals."""

from collections import defaultdict
from typing import Iterable, Sequence

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.forecaster import get_forecaster
from app.schemas.opportunity import OpportunityRecommendation
from app.schemas.portfolio import ConflictInsight
from app.services.portfolio import detect_conflicts


RANKER_VERSION = "policy-momentum-1.0"


async def rank_opportunities(
    opportunities: Sequence[OpportunityRecommendation],
    *,
    session: AsyncSession | None = None,
    horizon_days: int = 45,
) -> tuple[list[OpportunityRecommendation], dict[str, object]]:
    """Return enriched opportunity recommendations ordered by composite score."""

    if not opportunities:
        return [], {
            "ranker_version": RANKER_VERSION,
            "scoring_notes": "No opportunities supplied to ranker; response left empty.",
            "coverage": 0,
        }

    forecaster = get_forecaster()
    ticker_to_sector: dict[str, str] = {}
    for opportunity in opportunities:
        ticker = opportunity.ticker.upper()
        sector = forecaster.resolve_sector_for_ticker(ticker) or "Technology"
        ticker_to_sector[ticker] = sector

    forecast_map: dict[str, dict[str, object]] = {}
    sector_drivers: dict[str, list[str]] = {}
    sector_methodology: dict[str, str] = {}
    for sector, tickers in _group_by_sector(ticker_to_sector).items():
        try:
            bundle = await forecaster.forecast_sector(
                sector=sector,
                horizon_days=horizon_days,
                tickers=tickers,
            )
        except Exception as exc:  # pragma: no cover - defensive log
            logger.warning('Opportunity ranker failed to fetch forecast for %s: %s', sector, exc)
            continue
        sector_drivers[sector] = bundle.drivers
        sector_methodology[sector] = bundle.methodology_summary
        for signal in bundle.signals:
            forecast_map[signal.ticker.upper()] = {
                "expected_return_pct": signal.expected_return_pct,
                "confidence": signal.confidence,
                "catalysts": signal.catalysts,
                "thesis": signal.thesis,
            }

    conflicts = await _load_conflicts(session=session)
    conflict_map: dict[str, list[ConflictInsight]] = defaultdict(list)
    for conflict in conflicts:
        conflict_map[conflict.ticker.upper()].append(conflict)

    ranked: list[tuple[float, OpportunityRecommendation]] = []
    aggregated_drivers: list[str] = []

    for opportunity in opportunities:
        ticker = opportunity.ticker.upper()
        sector = ticker_to_sector.get(ticker, "Technology")
        forecast = forecast_map.get(ticker)
        conflict_insights = conflict_map.get(ticker)

        expected_return = forecast["expected_return_pct"] if forecast else opportunity.expected_return_pct
        forecast_confidence = forecast["confidence"] if forecast else 0.55

        policy_alignment = _policy_alignment(expected_return, forecast_confidence)
        conflict_score = _conflict_score(conflict_insights)
        composite_score = _composite_score(policy_alignment, opportunity.conviction, conflict_score)

        driver_candidates = forecast.get("catalysts", []) if forecast else []
        sector_driver_candidates = sector_drivers.get(sector, [])
        combined_drivers = _merge_drivers(driver_candidates, sector_driver_candidates)
        aggregated_drivers.extend(combined_drivers)

        conflict_details = _conflict_details(conflict_insights)
        explanation = _build_explanation(policy_alignment, conflict_score, combined_drivers, conflict_details)

        updated = opportunity.model_copy(
            update={
                "policy_alignment": round(policy_alignment, 4),
                "policy_alpha": round(expected_return, 2) if forecast else None,
                "conflict_score": round(conflict_score, 4) if conflict_score else 0.0,
                "composite_score": round(composite_score, 4),
                "drivers": combined_drivers or None,
                "conflict_insights": conflict_details or None,
                "explanation": explanation,
                "methodology": sector_methodology.get(sector),
            }
        )
        ranked.append((composite_score, updated))

    ranked.sort(key=lambda item: item[0], reverse=True)
    ordered = [item[1] for item in ranked]

    metadata = {
        "ranker_version": RANKER_VERSION,
        "scoring_notes": (
            "Composite score = 55% policy alignment + 35% conviction + 10% baseline, "
            "dampened by conflict risk up to 50%."
        ),
        "coverage": len(forecast_map),
        "top_drivers": _unique_preserve_order(aggregated_drivers)[:5],
    }
    return ordered, metadata


def _group_by_sector(ticker_to_sector: dict[str, str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for ticker, sector in ticker_to_sector.items():
        groups[sector].append(ticker)
    return groups


async def _load_conflicts(*, session: AsyncSession | None) -> list[ConflictInsight]:
    try:
        return await detect_conflicts(limit=50, session=session)
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.warning('Opportunity ranker using fallback conflict insights: %s', exc)
        return await detect_conflicts(limit=50)


def _normalize_return(value: float) -> float:
    return max(-1.0, min(1.0, value / 12.0))


def _policy_alignment(expected_return: float, confidence: float) -> float:
    normalized = _normalize_return(expected_return)
    score = normalized * 0.6 + confidence * 0.4
    return max(0.0, min(1.0, score))


def _conflict_score(conflicts: Iterable[ConflictInsight] | None) -> float:
    if not conflicts:
        return 0.0
    max_risk = max(conflict.risk_score for conflict in conflicts)
    return max(0.0, min(1.0, max_risk))


def _composite_score(policy_alignment: float, conviction: float, conflict_score: float) -> float:
    base = policy_alignment * 0.55 + conviction * 0.35 + 0.1
    dampened = base * (1 - conflict_score * 0.5)
    return max(0.0, min(1.0, dampened))


def _merge_drivers(*driver_groups: Iterable[str]) -> list[str]:
    return _unique_preserve_order(
        driver for group in driver_groups for driver in group if driver
    )[:3]


def _unique_preserve_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def _conflict_details(conflicts: Iterable[ConflictInsight] | None) -> list[str]:
    if not conflicts:
        return []
    details: list[str] = []
    for conflict in conflicts:
        summary = (
            f"{conflict.member} {conflict.transaction_type.lower()} {conflict.ticker} "
            f"({conflict.risk_score:.0%} risk)"
        )
        if conflict.bill_title:
            summary += f" linked to {conflict.bill_title}"
        details.append(summary)
    return details[:3]


def _build_explanation(
    policy_alignment: float,
    conflict_score: float,
    drivers: list[str],
    conflict_details: list[str],
) -> str:
    parts: list[str] = [f"Policy alignment contributes {policy_alignment:.0%} to the score."]
    if drivers:
        parts.append(f"Top drivers: {', '.join(drivers)}.")
    if conflict_details:
        parts.append(f"Conflict watch: {conflict_details[0]}.")
    if conflict_score:
        parts.append(f"Conflict dampener applied at {conflict_score:.0%}.")
    return ' '.join(parts)
