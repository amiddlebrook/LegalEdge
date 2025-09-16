"""Static overview data service."""
from loguru import logger

from app.schemas.overview import FeatureBlock, HeroHighlight, MetricBlock, OverviewPayload, WorkflowStep


async def get_product_overview() -> OverviewPayload:
    logger.debug("Generating product overview payload")
    """Return a curated payload describing the LegalEdge offering."""

    hero = HeroHighlight(
        kicker="Real-time policy intelligence",
        headline="LegalEdge brings predictive clarity to regulatory change.",
        subheadline=(
            "Connect legislation, regulatory actions, and congressional trades to understand how policy shifts "
            "will reverberate across portfolios before the market reacts."
        ),
        callouts=[
            "Continuously ingest cross-jurisdiction updates with minute-level latency.",
            "Correlate policy text with market performance signals and sector exposure.",
            "Integrate congressional trading activity into actionable recommendations.",
        ],
    )

    features = [
        FeatureBlock(
            title="Legislative Tracking",
            description=(
                "Monitor bills, committees, and regulatory actions across federal, state, and local jurisdictions."
            ),
            items=[
                "Real-time ingestion from congress.gov and state portals",
                "Policy heat-maps segmented by sector",
                "Committee workflows with auto-prioritization",
            ],
        ),
        FeatureBlock(
            title="AI-Powered Forecasting",
            description=(
                "Transformer models correlate policy language with historical market responses to surface predictive insights."
            ),
            items=[
                "Context aware embeddings and scenario simulation",
                "Ticker, sector, and thematic exposure scoring",
                "Confidence curves delivered through the API",
            ],
        ),
        FeatureBlock(
            title="Congressional Portfolio Tracker",
            description=(
                "Track and normalize congressional trades to reveal possible conflicts or early market signals."
            ),
            items=[
                "Automatic pairing of disclosures with pending legislation",
                "Conflict alerts for client portfolios",
                "Audit-ready history with SOC2-aligned retention",
            ],
        ),
    ]

    metrics = [
        MetricBlock(
            label="Prediction Accuracy Goal",
            value="70%+",
            helper="Target precision for market impact forecasts",
        ),
        MetricBlock(
            label="Retention Target",
            value="85%+",
            helper="Annual customer retention objective",
        ),
        MetricBlock(
            label="Processing SLA",
            value="< 5 min",
            helper="Legislation ingestion-to-insight target",
        ),
    ]

    workflow = [
        WorkflowStep(
            title="Ingest",
            body=(
                "Stream legislative updates, regulatory notices, and disclosure filings into a normalized warehouse."
            ),
        ),
        WorkflowStep(
            title="Enrich",
            body=(
                "Apply NLP entity extraction, labeling, and market correlation scoring for every policy object."
            ),
        ),
        WorkflowStep(
            title="Forecast",
            body=(
                "Run transformer-based models to project outcomes and quantify risk-adjusted opportunities."
            ),
        ),
        WorkflowStep(
            title="Act",
            body=(
                "Deliver alerts, API payloads, and dashboard updates tailored to venture, hedge, and retail personas."
            ),
        ),
    ]

    return OverviewPayload(
        hero=hero,
        data_sources=[
            "congress.gov",
            "State Legislature APIs",
            "SEC Form 4 & 13D",
            "News & RSS Feeds",
            "Custom client uploads",
        ],
        features=features,
        metrics=metrics,
        workflow=workflow,
    )