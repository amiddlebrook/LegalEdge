"""Persistence helpers for ingestion artifacts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Iterable, Sequence

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legislation import LegislativeBill, LegislativeBillVersion
from app.schemas.ingestion import IngestionArtifact, IngestionBatch


@dataclass
class NormalizationSummary:
    """Summary of ingestion normalization results."""

    total_received: int = 0
    legislation_processed: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    versions_created: int = 0

    @property
    def total_persisted(self) -> int:
        return self.created + self.updated


def _normalize_timestamp(value: datetime) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)



def _derive_next_action(artifact: IngestionArtifact) -> date | None:
    candidate = (
        artifact.metadata.get('hearing_date')
        or artifact.metadata.get('next_action_date')
        or artifact.metadata.get('vote_date')
    )
    if not candidate:
        if artifact.introduced_at is not None:
            return artifact.introduced_at.date()
        return None
    try:
        if isinstance(candidate, str):
            parsed = datetime.fromisoformat(candidate)
        elif isinstance(candidate, datetime):
            parsed = candidate
        else:
            return None
    except ValueError:
        logger.debug('Unable to parse next action date for %s from %s', artifact.external_id, candidate)
        return None
    parsed = _normalize_timestamp(parsed)
    return parsed.date()


def _payload_from_bill(bill: LegislativeBill) -> dict[str, object]:
    return {
        'bill_id': bill.bill_id,
        'title': bill.title,
        'stage': bill.stage,
        'jurisdiction': bill.jurisdiction,
        'committees': bill.committees or [],
        'sectors': bill.sectors or [],
        'summary': bill.summary,
        'next_action_date': bill.next_action_date.isoformat() if bill.next_action_date else None,
        'sentiment_score': bill.sentiment_score,
        'probability_of_enactment': bill.probability_of_enactment,
        'last_updated': bill.last_updated.isoformat() if bill.last_updated else None,
    }


def _merge_list(existing: list[str] | None, incoming: list[str]) -> list[str]:
    base = existing or []
    merged = sorted({item.strip() for item in base + incoming if item})
    return merged


async def _record_version(session: AsyncSession, bill: LegislativeBill) -> None:
    result = await session.execute(
        select(func.max(LegislativeBillVersion.version)).where(
            LegislativeBillVersion.bill_id == bill.bill_id
        )
    )
    current_version = result.scalar() or 0
    session.add(
        LegislativeBillVersion(
            bill_id=bill.bill_id,
            version=current_version + 1,
            payload=_payload_from_bill(bill),
        )
    )


async def persist_artifacts(
    artifacts: Iterable[IngestionArtifact],
    session: AsyncSession,
) -> NormalizationSummary:
    items = list(artifacts)
    summary = NormalizationSummary(total_received=len(items))

    legislative = [item for item in items if str(item.artifact_type).lower() == 'legislation']
    summary.legislation_processed = len(legislative)

    if not legislative:
        return summary

    bill_ids = [artifact.external_id.upper() for artifact in legislative]
    existing: dict[str, LegislativeBill] = {}
    if bill_ids:
        result = await session.execute(
            select(LegislativeBill).where(LegislativeBill.bill_id.in_(bill_ids))
        )
        existing = {bill.bill_id: bill for bill in result.scalars().all()}

    for artifact in legislative:
        bill_id = artifact.external_id.upper()
        next_action = _derive_next_action(artifact)
        committees = _merge_list(None, artifact.committees)
        sectors = _merge_list(None, artifact.sectors)
        last_updated = _normalize_timestamp(artifact.last_updated)

        bill = existing.get(bill_id)
        if bill is None:
            bill = LegislativeBill(
                bill_id=bill_id,
                title=artifact.title,
                stage=artifact.stage or 'Introduced',
                jurisdiction=artifact.jurisdiction,
                committees=committees,
                sectors=sectors,
                summary=artifact.summary,
                next_action_date=next_action,
                last_updated=last_updated,
            )
            session.add(bill)
            await session.flush()
            await _record_version(session, bill)
            summary.created += 1
            summary.versions_created += 1
            existing[bill_id] = bill
            continue

        changed = False
        if artifact.title and artifact.title != bill.title:
            bill.title = artifact.title
            changed = True
        if artifact.stage and artifact.stage != bill.stage:
            bill.stage = artifact.stage
            changed = True
        if artifact.summary and artifact.summary != bill.summary:
            bill.summary = artifact.summary
            changed = True
        if artifact.jurisdiction and artifact.jurisdiction != bill.jurisdiction:
            bill.jurisdiction = artifact.jurisdiction
            changed = True

        merged_committees = _merge_list(bill.committees, committees)
        if merged_committees != (bill.committees or []):
            bill.committees = merged_committees
            changed = True

        merged_sectors = _merge_list(bill.sectors, sectors)
        if merged_sectors != (bill.sectors or []):
            bill.sectors = merged_sectors
            changed = True

        if next_action and next_action != bill.next_action_date:
            bill.next_action_date = next_action
            changed = True

        existing_last_updated = _normalize_timestamp(bill.last_updated)
        if last_updated > existing_last_updated:
            bill.last_updated = last_updated
            changed = True
        else:
            bill.last_updated = existing_last_updated

        if changed:
            await session.flush()
            await _record_version(session, bill)
            summary.updated += 1
            summary.versions_created += 1
        else:
            summary.skipped += 1

    if summary.created or summary.updated:
        await session.commit()
        logger.info(
            'Persisted %s legislative artifacts (%s created, %s updated, %s versions)',
            summary.legislation_processed,
            summary.created,
            summary.updated,
            summary.versions_created,
        )
    elif session.in_transaction():
        await session.rollback()

    return summary


async def persist_batches(
    batches: Sequence[IngestionBatch],
    session: AsyncSession,
) -> NormalizationSummary:
    artifacts: list[IngestionArtifact] = []
    for batch in batches:
        artifacts.extend(batch.artifacts)
    if not artifacts:
        return NormalizationSummary()
    return await persist_artifacts(artifacts, session=session)


__all__ = ['NormalizationSummary', 'persist_artifacts', 'persist_batches']
