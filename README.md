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
## Background Workers

LegalEdge uses Celery for robust background task processing with Redis as the message broker.

### Setup

1. **Using Docker Compose** (Recommended):
```bash
docker-compose up postgres redis
```

2. **Manual Setup**:
```bash
# Start Redis
redis-server

# Start PostgreSQL (if not using Docker)
# Configure your PostgreSQL instance with the connection string in .env
```

### Running Workers

```bash
# Run Celery worker
python -m app.workers.cli worker

# Run Celery beat scheduler
python -m app.workers.cli beat

# Run Flower monitoring interface
python -m app.workers.cli flower

# Run specific tasks manually
python -m app.workers.cli task ingestion
```

### Scheduled Tasks

- **Ingestion**: Runs every 6 hours to fetch legislative data
- **Model Retraining**: Legislation models every 12 hours, forecasting models every 6 hours
- **Alert Processing**: Processes pending alerts every 5 minutes
- **Data Cleanup**: Cleans old audit logs daily at 2 AM
- **Market Snapshots**: Generates market analysis every 2 hours

### Task Management API

- `GET /api/v1/tasks/status` - Get worker queue status
- `POST /api/v1/tasks/ingestion/run` - Manually trigger ingestion
- `GET /api/v1/tasks/ingestion/history` - Get ingestion task history
- `POST /api/v1/tasks/models/retrain/legislation` - Retrain legislation models
- `POST /api/v1/tasks/models/retrain/forecasting` - Retrain forecasting models
- `GET /api/v1/tasks/scheduled` - Get scheduled tasks information

### Monitoring

Access Flower monitoring interface at `http://localhost:5555` when running with Docker Compose.

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
- `GET /api/v1/legislation/upcoming` - mock legislative feed for UI prototyping.
- Background ingestion is orchestrated by a recurring task manager during application lifespan events.