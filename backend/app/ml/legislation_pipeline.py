from __future__ import annotations

"""Legislation NLP pipeline with transformer-aware fallbacks."""

import asyncio
import math
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Iterable

import httpx
from loguru import logger

__all__ = [
    'LegislationNlpPipeline',
    'LegislationNlpResult',
    'get_pipeline',
]

_TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z\-'&]+")
_POSITIVE_LEXICON: dict[str, float] = {
    'accelerate': 0.6,
    'incentive': 0.9,
    'grant': 1.1,
    'funding': 1.2,
    'investment': 1.0,
    'modernization': 0.8,
    'streamlined': 0.7,
    'support': 0.5,
    'expansion': 0.6,
    'innovation': 0.9,
    'resilience': 0.7,
    'partnership': 0.6,
    'infrastructure': 0.8,
}
_NEGATIVE_LEXICON: dict[str, float] = {
    'penalty': 1.1,
    'moratorium': 1.4,
    'ban': 1.5,
    'prohibit': 1.3,
    'restriction': 1.1,
    'suspension': 1.0,
    'compliance burden': 1.0,
    'fine': 1.0,
    'enforcement action': 1.2,
    'sanction': 1.3,
    'liability': 1.0,
    'delay': 0.7,
}
_MOMENTUM_LEXICON: dict[str, float] = {
    'bipartisan': 1.4,
    'fast-track': 1.5,
    'unanimous': 1.2,
    'committee report': 0.9,
    'markup': 0.7,
    'floor vote': 1.4,
    'companion bill': 0.8,
    'lead sponsor': 0.6,
    'whip count': 0.9,
    'executive support': 1.3,
    'stakeholder coalition': 1.0,
}
_DRAG_LEXICON: dict[str, float] = {
    'controversial': 1.2,
    'lawsuit': 1.4,
    'opposition': 1.1,
    'veto threat': 1.5,
    'procedural challenge': 1.5,
    'hold': 0.8,
    'delay': 0.8,
    'poison pill': 1.3,
    'litigation': 1.3,
}
_COMPLIANCE_LEXICON: dict[str, float] = {
    'reporting': 0.7,
    'audit': 0.9,
    'attestation': 1.1,
    'disclosure': 0.6,
    'risk management': 0.8,
    'internal control': 0.7,
    'penalty': 1.0,
    'obligation': 0.6,
    'compliance': 0.5,
    'oversight': 0.5,
}
_SECTOR_KEYWORDS: dict[str, tuple[str, ...]] = {
    'technology': ('ai', 'artificial intelligence', 'software', 'cybersecurity', 'data', 'cloud'),
    'financial services': ('fintech', 'banks', 'lending', 'compliance', 'regtech', 'securities'),
    'healthcare': ('biotech', 'clinical', 'medicare', 'telehealth', 'pharma', 'life sciences'),
    'energy': ('grid', 'renewable', 'utility', 'transmission', 'infrastructure', 'resilience'),
    'defense': ('national security', 'defense', 'dod', 'contractor', 'federal procurement'),
    'infrastructure': ('transportation', 'ports', 'highway', 'bridge', 'water systems'),
}
_TICKER_SECTOR_MAP: dict[str, str] = {
    'AIT': 'technology',
    'GRID': 'energy',
    'REGN': 'financial services',
    'CSPN': 'technology',
    'EVGR': 'infrastructure',
}


@dataclass(slots=True)
class LegislationNlpResult:
    """Structured output from the legislation NLP pipeline."""

    sentiment: float
    enactment_probability: float
    ticker_impacts: dict[str, float]
    sector_impacts: dict[str, float]
    confidence: float
    rationale: str
    drivers: list[str] = field(default_factory=list)
    diagnostics: dict[str, object] = field(default_factory=dict)
    model_version: str = '0.0.1'


class LegislationNlpPipeline:
    """Hybrid legislation analysis pipeline with optional transformer inference."""

    def __init__(
        self,
        *,
        http_client_factory: Callable[[], httpx.AsyncClient] | None = None,
        enable_transformers: bool | None = None,
    ) -> None:
        self._client_factory = http_client_factory or (lambda: httpx.AsyncClient(timeout=5.0, follow_redirects=True))
        self._enable_transformers = enable_transformers
        if self._enable_transformers is None:
            self._enable_transformers = os.getenv('LEGALEDGE_ENABLE_TRANSFORMERS', '').lower() in {'1', 'true', 'yes'}
        self._model_version = self._stamp_version()
        self._sentiment_bias = 0.05
        self._enactment_bias = 0.12
        self._last_retrained = datetime.now(timezone.utc)
        self._transformer_lock = asyncio.Lock()
        self._sentiment_pipeline = None

    async def analyze(self, synopsis: str, *, bill_id: str, target_tickers: Iterable[str], full_text: str | None = None,
                      risk_appetite: str = 'balanced') -> LegislationNlpResult:
        """Return a deterministic market impact projection from bill language."""

        document = self._coalesce_text(synopsis, full_text)
        tokens = _TOKEN_PATTERN.findall(document.lower())
        token_count = max(1, len(tokens))

        positive_score, positive_hits = _lexicon_score(document, _POSITIVE_LEXICON)
        negative_score, negative_hits = _lexicon_score(document, _NEGATIVE_LEXICON)
        momentum_score, momentum_hits = _lexicon_score(document, _MOMENTUM_LEXICON)
        drag_score, drag_hits = _lexicon_score(document, _DRAG_LEXICON)
        compliance_score, compliance_hits = _lexicon_score(document, _COMPLIANCE_LEXICON)

        heuristic_sentiment = self._heuristic_sentiment(
            positive_score=positive_score,
            negative_score=negative_score,
            token_count=token_count,
        )
        transformer_sentiment = await self._transformer_sentiment(document)
        sentiment = self._blend_sentiment(heuristic_sentiment, transformer_sentiment)

        enactment_probability = self._enactment_probability(
            momentum_score=momentum_score,
            drag_score=drag_score,
            compliance_score=compliance_score,
            sentiment=sentiment,
            risk_appetite=risk_appetite,
        )

        sector_scores = self._sector_scores(document)
        ticker_impacts = self._ticker_impacts(
            target_tickers,
            sentiment=sentiment,
            enactment_probability=enactment_probability,
            compliance_score=compliance_score,
            sector_scores=sector_scores,
            document=document,
        )

        confidence = self._confidence(
            sentiment=sentiment,
            enactment_probability=enactment_probability,
            momentum_score=momentum_score,
            drag_score=drag_score,
            compliance_score=compliance_score,
            token_count=token_count,
        )

        drivers = self._drivers(
            positive_hits=positive_hits,
            negative_hits=negative_hits,
            momentum_hits=momentum_hits,
            drag_hits=drag_hits,
            compliance_hits=compliance_hits,
            sector_scores=sector_scores,
        )

        rationale = self._rationale(
            bill_id=bill_id,
            sentiment=sentiment,
            enactment_probability=enactment_probability,
            top_driver=drivers[0] if drivers else 'market structure language',
        )

        diagnostics = {
            'positive_score': round(positive_score, 3),
            'negative_score': round(negative_score, 3),
            'momentum_score': round(momentum_score, 3),
            'drag_score': round(drag_score, 3),
            'compliance_score': round(compliance_score, 3),
            'token_count': token_count,
            'transformer_applied': transformer_sentiment is not None,
        }

        return LegislationNlpResult(
            sentiment=round(sentiment, 4),
            enactment_probability=round(enactment_probability, 4),
            ticker_impacts=ticker_impacts,
            sector_impacts=self._normalize_sector_impacts(sector_scores, sentiment),
            confidence=round(confidence, 4),
            rationale=rationale,
            drivers=drivers,
            diagnostics=diagnostics,
            model_version=self._model_version,
        )

    async def retrain(self) -> None:
        """Simulate scheduled retraining by recalibrating internal biases."""

        self._model_version = self._stamp_version()
        horizon = (datetime.now(timezone.utc) - self._last_retrained).total_seconds() or 1.0
        adjustment = math.tanh(horizon / 86_400.0) * 0.05
        self._sentiment_bias = 0.05 + adjustment
        self._enactment_bias = 0.12 + adjustment * 0.8
        self._last_retrained = datetime.now(timezone.utc)
        logger.debug('Legislation NLP pipeline retrained; new version %s', self._model_version)

    async def fetch_full_text(self, url: str) -> str | None:
        """Fetch the full bill text when a URL is provided."""

        try:
            async with self._client_factory() as client:
                response = await client.get(url)
                response.raise_for_status()
                snippet = response.text.strip()
                if snippet:
                    return snippet
        except Exception as exc:  # pragma: no cover - network dependent
            logger.debug('Unable to retrieve bill text from %s (%s)', url, exc)
        return None

    @staticmethod
    def _coalesce_text(synopsis: str, full_text: str | None) -> str:
        parts = [synopsis.strip() or '']
        if full_text:
            parts.append(full_text.strip())
        return '\n'.join(part for part in parts if part)

    def _heuristic_sentiment(self, *, positive_score: float, negative_score: float, token_count: int) -> float:
        balance = positive_score - negative_score
        magnitude = positive_score + negative_score + 1.0
        normalized = balance / magnitude
        scaled = math.tanh(normalized * 2.5 + self._sentiment_bias)
        return float(max(-1.0, min(1.0, scaled)))

    async def _transformer_sentiment(self, document: str) -> float | None:
        if not self._enable_transformers:
            return None
        async with self._transformer_lock:
            if self._sentiment_pipeline is None:
                try:
                    from transformers import pipeline  # type: ignore
                except Exception as exc:  # pragma: no cover - optional dependency
                    logger.warning('Transformer libraries unavailable: %s', exc)
                    self._enable_transformers = False
                    return None
                loop = asyncio.get_running_loop()
                self._sentiment_pipeline = await loop.run_in_executor(
                    None,
                    lambda: pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english'),
                )
        if self._sentiment_pipeline is None:
            return None
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, lambda: self._sentiment_pipeline(document[:512]))
        try:
            payload = result[0]
            label = (payload['label'] or '').lower()
            score = float(payload['score'])
            if label.startswith('neg'):
                score = -score
            return max(-1.0, min(1.0, score))
        except Exception:  # pragma: no cover - defensive fallback
            return None

    @staticmethod
    def _blend_sentiment(heuristic: float, transformer: float | None) -> float:
        if transformer is None:
            return heuristic
        return max(-1.0, min(1.0, heuristic * 0.6 + transformer * 0.4))

    def _enactment_probability(
        self,
        *,
        momentum_score: float,
        drag_score: float,
        compliance_score: float,
        sentiment: float,
        risk_appetite: str,
    ) -> float:
        base = momentum_score - drag_score
        compliance_drag = compliance_score * 0.15
        sentiment_lift = sentiment * 0.4
        raw_score = base * 0.35 + sentiment_lift - compliance_drag + self._enactment_bias
        probability = 1.0 / (1.0 + math.exp(-raw_score))
        appetite = risk_appetite.lower()
        if appetite == 'conservative':
            probability *= 0.9
        elif appetite == 'aggressive':
            probability = min(0.99, probability * 1.08)
        return float(max(0.01, min(0.99, probability)))

    def _sector_scores(self, document: str) -> dict[str, float]:
        lowered = document.lower()
        scores: dict[str, float] = {}
        for sector, keywords in _SECTOR_KEYWORDS.items():
            score = 0.0
            for keyword in keywords:
                score += len(re.findall(rf'\b{re.escape(keyword)}\b', lowered))
            if score:
                scores[sector] = score
        return scores

    def _ticker_impacts(
        self,
        tickers: Iterable[str],
        *,
        sentiment: float,
        enactment_probability: float,
        compliance_score: float,
        sector_scores: dict[str, float],
        document: str,
    ) -> dict[str, float]:
        impacts: dict[str, float] = {}
        lowered = document.lower()
        max_sector_score = max(sector_scores.values(), default=1.0)
        compliance_drag = min(0.35, compliance_score * 0.05)
        for ticker_raw in tickers:
            ticker = ticker_raw.upper()
            if not ticker:
                continue
            sector = _TICKER_SECTOR_MAP.get(ticker)
            if sector is None and sector_scores:
                sector = max(sector_scores, key=sector_scores.get)
            sector_score = sector_scores.get(sector, 0.3)
            ticker_mentions = len(re.findall(rf'\b{re.escape(ticker.lower())}\b', lowered))
            presence_multiplier = 1.0 + min(0.35, ticker_mentions * 0.12)
            sector_multiplier = 1.0 + (sector_score / max_sector_score) * 0.25
            base_move = sentiment * 0.05
            enactment_multiplier = 0.45 + enactment_probability * 0.65
            movement = base_move * enactment_multiplier * presence_multiplier * sector_multiplier * (1.0 - compliance_drag)
            movement = max(-0.14, min(0.14, movement))
            impacts[ticker] = round(movement, 4)
        return impacts

    @staticmethod
    def _normalize_sector_impacts(sector_scores: dict[str, float], sentiment: float) -> dict[str, float]:
        if not sector_scores:
            return {}
        total = sum(sector_scores.values()) or 1.0
        return {
            sector: round(sentiment * (score / total), 4)
            for sector, score in sector_scores.items()
        }

    @staticmethod
    def _confidence(
        *,
        sentiment: float,
        enactment_probability: float,
        momentum_score: float,
        drag_score: float,
        compliance_score: float,
        token_count: int,
    ) -> float:
        coverage_factor = min(1.0, token_count / 600.0)
        volatility_penalty = min(0.25, compliance_score * 0.03 + drag_score * 0.04)
        momentum_edge = min(0.25, momentum_score * 0.04)
        base = 0.4 + abs(sentiment) * 0.2 + enactment_probability * 0.25 + momentum_edge
        confidence = base * coverage_factor - volatility_penalty
        return float(max(0.2, min(0.92, confidence)))

    @staticmethod
    def _drivers(
        *,
        positive_hits: dict[str, int],
        negative_hits: dict[str, int],
        momentum_hits: dict[str, int],
        drag_hits: dict[str, int],
        compliance_hits: dict[str, int],
        sector_scores: dict[str, float],
    ) -> list[str]:
        drivers: list[str] = []
        if positive_hits:
            top = ', '.join(_top_terms(positive_hits, limit=3))
            drivers.append(f"Pro-growth language: {top}")
        if momentum_hits:
            top = ', '.join(_top_terms(momentum_hits, limit=2))
            drivers.append(f"Momentum signals: {top}")
        if negative_hits:
            top = ', '.join(_top_terms(negative_hits, limit=2))
            drivers.append(f"Risk factors cited: {top}")
        if compliance_hits:
            top = ', '.join(_top_terms(compliance_hits, limit=2))
            drivers.append(f"Compliance focus: {top}")
        if drag_hits:
            top = ', '.join(_top_terms(drag_hits, limit=2))
            drivers.append(f"Political headwinds: {top}")
        if sector_scores:
            top_sector = max(sector_scores, key=sector_scores.get)
            drivers.append(f"Primary sector exposure: {top_sector.title()}")
        return drivers

    @staticmethod
    def _rationale(*, bill_id: str, sentiment: float, enactment_probability: float, top_driver: str) -> str:
        tone = 'constructive' if sentiment >= 0.15 else 'balanced' if sentiment >= -0.1 else 'defensive'
        return (
            f"Analysis for {bill_id} indicates a {tone} tone with {enactment_probability:.0%} enactment odds. "
            f"Key driver: {top_driver.lower()}."
        )

    @staticmethod
    def _stamp_version() -> str:
        return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _lexicon_score(text: str, lexicon: dict[str, float]) -> tuple[float, dict[str, int]]:
    lowered = text.lower()
    score = 0.0
    hits: dict[str, int] = {}
    for phrase, weight in lexicon.items():
        pattern = re.compile(rf'\b{re.escape(phrase)}\b', re.IGNORECASE)
        matches = pattern.findall(lowered)
        if matches:
            hits[phrase] = len(matches)
            score += weight * len(matches)
    return score, hits


def _top_terms(hits: dict[str, int], *, limit: int) -> list[str]:
    return [term for term, _ in sorted(hits.items(), key=lambda item: (-item[1], item[0]))[:limit]]


_PIPELINE: LegislationNlpPipeline | None = None


def get_pipeline() -> LegislationNlpPipeline:
    """Return a singleton instance of the legislation NLP pipeline."""

    global _PIPELINE
    if _PIPELINE is None:
        _PIPELINE = LegislationNlpPipeline()
    return _PIPELINE
