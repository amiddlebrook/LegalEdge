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

- `legislation` – ingesting and analyzing bills, resolutions, and regulatory items.
- `forecasts` – surfacing AI-driven predictive signals tied to sectors and tickers.
- `portfolios` – correlating congressional trades with pending policy for conflict insights.

## Project structure

```
app/
  api/          # FastAPI routers
  core/         # Configuration and settings
  db/           # Database session factories
  schemas/      # Pydantic models shared by the API and services
  services/     # Domain services (ingestion, forecasting, portfolio tracking)
  workflows/    # Orchestration entry points for background tasks
```

The service is prepared for PostgreSQL via SQLAlchemy async sessions. Update the connection string via `.env` or environment variables prefixed with `LEGALEDGE_`.## Background ingestion

A recurring task manager triggers `run_daily_ingestion` on startup based on `LEGALEDGE_INGESTION_SCHEDULE_MINUTES`. The stub logs activity for now and is ready to orchestrate Prefect, Celery, or AWS-native jobs once real data pipelines are wired.## Logging

Loguru is installed as the unified logging sink. `configure_logging()` intercepts Uvicorn/FastAPI loggers so background tasks and API handlers emit consistent structured logs.