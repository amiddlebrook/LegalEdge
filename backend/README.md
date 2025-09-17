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

Repository helpers in `app/repositories` provide async query utilities and will back future ingestion pipelines.

## Background ingestion

A recurring task manager triggers `run_daily_ingestion` on startup based on `LEGALEDGE_INGESTION_SCHEDULE_MINUTES`. The stub logs activity for now and is ready to orchestrate Prefect, Celery, or AWS-native jobs once real data pipelines are wired.

## Logging

Loguru is installed as the unified logging sink. `configure_logging()` intercepts Uvicorn/FastAPI loggers so background tasks and API handlers emit consistent structured logs.## Sample data

Populate the development database with representative records by running:

```bash
python -m app.ingestion.sample_data --reset
```

The command uses the configured `LEGALEDGE_DATABASE_URL` and seeds legislation, forecast, and trade tables for local testing.