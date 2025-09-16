"""Product overview schemas."""
from pydantic import BaseModel


class HeroHighlight(BaseModel):
    """Landing page hero copy and supporting callouts."""

    kicker: str
    headline: str
    subheadline: str
    callouts: list[str]


class FeatureBlock(BaseModel):
    """Feature pillar card content."""

    title: str
    description: str
    items: list[str]


class MetricBlock(BaseModel):
    """Success metric card."""

    label: str
    value: str
    helper: str


class WorkflowStep(BaseModel):
    """High-level step in the platform workflow."""

    title: str
    body: str


class OverviewPayload(BaseModel):
    """Aggregate payload powering the marketing/overview experience."""

    hero: HeroHighlight
    data_sources: list[str]
    features: list[FeatureBlock]
    metrics: list[MetricBlock]
    workflow: list[WorkflowStep]