# LegalEdge Platform

Initial scaffolding for LegalEdge - an AI-driven legislative intelligence and investment insights platform.

## Structure

- `backend/` - FastAPI service prepared for PostgreSQL, async SQLAlchemy, and AI/ML orchestration placeholders.
- `frontend/` - React + TailwindCSS client highlighting the product pillars, success metrics, and workflow.
- `LegalEdge_Final.pdf` - Source product brief.

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Next steps

1. Connect external data sources (congress.gov, SEC, state portals) to replace stub services.
2. Implement transformer-based NLP pipelines for legislation analysis and forecasting accuracy targets.
3. Stand up PostgreSQL schemas and background ingestion workers (Celery/Prefect/AWS Lambda).
4. Harden authentication with OAuth 2.0 and instrument SOC2-aligned logging and monitoring.

### API surface

- `GET /api/v1/overview` - returns hero copy, feature pillars, metrics, and workflow data consumed by the React client.
- `GET /api/v1/dashboard/snapshot` - aggregates legislation, forecast, and portfolio signals for the investor view.
- `GET /api/v1/opportunities` - market opportunity engine recommendations.
- `GET /api/v1/alerts` - policy and trading alerts feed.
- `GET /api/v1/health/status` - simple liveness probe for infra checks.
- `GET /api/v1/legislation/upcoming` - mock legislative feed for UI prototyping.\n- Background ingestion is orchestrated by a recurring task manager during application lifespan events.\n