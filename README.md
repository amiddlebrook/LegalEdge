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
npm run dev
```

## Deployment

### Quick Start (Development)
```bash
# Install dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# Start services with Docker Compose
docker-compose up postgres redis

# Run backend
cd backend && uvicorn app.main:app --reload

# Run frontend
cd frontend && npm run dev
```

### Production Deployment
```bash
# Build and deploy to AWS
cd infrastructure
terraform init
terraform plan -var="environment=production"
terraform apply

# Deploy application
aws ecs update-service --cluster legaledge-production-cluster \
  --service legaledge-production-app --force-new-deployment
```

### Infrastructure Components
- **ECS Fargate**: Container orchestration
- **RDS PostgreSQL**: Primary database
- **ElastiCache Redis**: Caching and sessions
- **S3**: Static assets and data storage
- **CloudFront**: CDN for global performance
- **Load Balancer**: Traffic distribution
- **VPC**: Secure network isolation

## Monitoring & Operations

### Health Checks
- **Application**: `/api/v1/health/status`
- **Load Balancer**: Target group health checks
- **Database**: Connection monitoring
- **Cache**: Redis connectivity

### Monitoring Dashboard
Access monitoring dashboards at:
- **Application Metrics**: CloudWatch Dashboard
- **Infrastructure**: AWS Console
- **Logs**: CloudWatch Logs Insights

### CI/CD Pipeline
Automated deployment via GitHub Actions:
- Code quality checks
- Security scanning
- Docker image building
- Infrastructure deployment
- Health verification

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

## API surface

- `GET /api/v1/overview` - returns hero copy, feature pillars, metrics, and workflow data consumed by the React client.
- `GET /api/v1/dashboard/snapshot` - aggregates legislation, forecast, and portfolio signals for the investor view.
- `GET /api/v1/opportunities` - market opportunity engine recommendations.
- `GET /api/v1/alerts` - policy and trading alerts feed.
- `GET /api/v1/health/status` - simple liveness probe for infra checks.
- `GET /api/v1/legislation/upcoming` - mock legislative feed for UI prototyping.
- Background ingestion is orchestrated by a recurring task manager during application lifespan events.