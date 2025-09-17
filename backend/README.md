# LegalEdge Backend

FastAPI service that powers legislative monitoring, AI forecasting, and the congressional portfolio tracker described in the LegalEdge product brief.

## Getting started

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is exposed under `/api/v1` and is organized around the core business capabilities:

- `legislation` - ingesting and analyzing bills, resolutions, and regulatory items.
- `forecasts` - surfacing AI-driven predictive signals tied to sectors and tickers.
- `portfolios` - correlating congressional trades with pending policy for conflict insights.


## API surface

- `GET /api/v1/overview` - hero copy, feature pillars, success metrics, and workflow data consumed by the React client.
- `GET /api/v1/dashboard/snapshot` - aggregates legislation, forecast, and portfolio signals for the investor view.
- `GET /api/v1/legislation/upcoming` - multi-jurisdiction legislative feed for UI prototyping and ingestion warmups.
- `GET /api/v1/opportunities` - market opportunity engine recommendations.
- `GET /api/v1/alerts` - policy and trading alerts feed with optional filtering (`categories`, `severities`, `min_severity`, `entity`, `since_minutes`).
- `GET /api/v1/coverage` - jurisdiction coverage, ingestion latency, and trade surveillance health.
- `GET /api/v1/entity-resolution/summary` - bill-to-ticker linkage coverage and resolution metrics.
- `GET /api/v1/health/status` - simple liveness probe for infra checks.


## Project structure

```
app/
  api/          # FastAPI routers
  core/         # Configuration, logging, and background tasks
  db/           # Database session factories
  models/       # SQLAlchemy ORM models
  repositories/ # Data access helpers
  schemas/      # Pydantic models shared by the API and services
  services/     # Domain services (ingestion, forecasting, portfolio tracking)
  workflows/    # Orchestration entry points for background tasks
```

The service is prepared for PostgreSQL via SQLAlchemy async sessions. Update the connection string via `.env` or environment variables prefixed with `LEGALEDGE_`.

## Data model

SQLAlchemy models live under `app/models` and cover:

- `LegislativeBill` – normalized legislation metadata, jurisdiction, sector tags, and scoring fields.
- `ForecastSignal` – sector/ticker forecasts with expected return, confidence, and catalysts.
- `TradeDisclosure` – congressional trade disclosures linked back to legislation when available.
- `PolicyAlert` – persisted alert feed items tying policy signals to entities.
- `OpportunityRecommendation` – market opportunity engine outputs with conviction, horizon, catalysts, and risk ratings.

Repository helpers in `app/repositories` provide async query utilities and will back future ingestion pipelines.

## Background ingestion

A recurring task manager triggers `run_daily_ingestion` on startup based on `LEGALEDGE_INGESTION_SCHEDULE_MINUTES`. When a database connection is configured, the task opens its own session (using `SessionLocal`) to exercise the ingestion pathways, paving the way for Prefect, Celery, or AWS-native jobs once real pipelines are wired.

## Logging

Loguru is installed as the unified logging sink. `configure_logging()` intercepts Uvicorn/FastAPI loggers so background tasks and API handlers emit consistent structured logs.

## Sample data

Populate the development database with representative records by running:

```bash
python -m app.ingestion.sample_data --reset
```

The command uses the configured `LEGALEDGE_DATABASE_URL` and seeds legislation, forecast, and trade tables for local testing.

## Migrations

Alembic is configured in `alembic.ini`. After installing requirements, create or upgrade the schema with:

```bash
cd backend
alembic upgrade head
```

Generate new migrations after model changes:

```bash
alembic revision --autogenerate -m "describe change"
```

The migration environment pulls the connection string from `LEGALEDGE_DATABASE_URL`.

## CLI utilities

Run project helpers with the management CLI:

```bash
python -m app.cli seed-sample-data --reset  # seed development fixtures
python -m app.cli run-ingestion-once       # trigger ingestion without waiting for the scheduler
```

The scheduler also invokes `run-ingestion-once` automatically on the configured cadence.


