# LegalEdge Platform 🚀

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.1.1-blue.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

**LegalEdge** is an AI-powered legislative intelligence platform that helps investors understand how legislation affects their portfolios and identify market opportunities driven by policy changes.

## 🎯 What is LegalEdge?

LegalEdge bridges the gap between legislative actions and investment decisions by providing:

- **📊 Portfolio Risk Analysis**: Real-time assessment of how legislation impacts your investments
- **🔮 AI-Powered Forecasting**: Machine learning models predict market movements based on policy signals
- **⚡ Smart Alerts**: Instant notifications when legislation affects your holdings
- **📈 Opportunity Discovery**: Identify investment opportunities created by regulatory changes
- **🔗 Conflict Detection**: Track congressional trades and potential conflicts of interest
- **📚 Comprehensive Coverage**: Monitor federal, state, and international legislative activities

## ✨ Key Features

### 🤖 AI & Machine Learning
- **Legislation NLP Pipeline**: Advanced natural language processing to analyze bill text and predict impact
- **Sector Forecasting**: Machine learning models predict market movements across 20+ sectors
- **Sentiment Analysis**: Real-time sentiment scoring of legislative language
- **Risk Assessment**: Automated risk scoring for portfolio positions

### 📊 Portfolio Intelligence
- **Real-time Monitoring**: Continuous tracking of legislative developments
- **Impact Scoring**: Quantified impact assessment for each holding
- **Sector Diversification**: Advanced portfolio diversification analysis
- **Performance Attribution**: Understand how policy affects your returns

### 🚨 Alert System
- **Customizable Alerts**: Set up alerts for specific topics, sectors, or companies
- **Multi-channel Notifications**: Email, SMS, webhook, and in-app notifications
- **Smart Filtering**: AI-powered relevance scoring reduces alert fatigue
- **Escalation Rules**: Critical alerts get priority treatment

### 🔧 Enterprise Features
- **API Access**: RESTful API for custom integrations
- **Bulk Operations**: Import/export large portfolios via CSV
- **Team Collaboration**: Shared portfolios and alert management
- **Audit Trails**: Complete activity logging for compliance

## 🏗️ Architecture

LegalEdge is built with a modern, scalable microservices architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                            LegalEdge Platform                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐  │
│  │   React     │  │   FastAPI   │  │   Celery    │  │  Redis  │  │
│  │  Frontend   │  │   Backend   │  │  Workers    │  │ Queue   │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐  │
│  │ PostgreSQL  │  │   ML/AI     │  │   External  │  │  Cache  │  │
│  │ Database    │  │   Models    │  │    APIs     │  │ Layer   │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Backend
- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL with async SQLAlchemy ORM
- **Task Queue**: Celery with Redis broker
- **ML/AI**: PyTorch, scikit-learn, transformers
- **Monitoring**: Structured logging with Loguru

#### Frontend
- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite for fast development
- **Styling**: TailwindCSS for responsive design
- **Charts**: Recharts for data visualization
- **State Management**: React Query for server state

#### DevOps & Infrastructure
- **Containerization**: Docker and Docker Compose
- **Deployment**: AWS ECS Fargate with Terraform
- **Monitoring**: CloudWatch, custom dashboards
- **CI/CD**: GitHub Actions with automated testing

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Git

### Local Development Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/amiddlebrook/LegalEdge.git
cd LegalEdge
```

#### 2. Backend Setup
```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
# Optional: Install ML dependencies
pip install -r requirements-ml.txt

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Run database migrations
alembic upgrade head

# Seed sample data (optional)
python -m app.cli seed-sample-data --reset

# Start the API server
uvicorn app.main:app --reload
```

#### 3. Frontend Setup
```bash
cd frontend
npm install

# Copy environment configuration
cp .env.example .env.local
# Edit .env.local to point to your backend

echo 'VITE_API_BASE_URL=http://localhost:8000/api/v1' > .env.local

# Start development server
npm run dev
```

#### 4. Start Services
```bash
# Start PostgreSQL and Redis
cd LegalEdge  # Back to project root
docker-compose up postgres redis -d

# Optional: Start background workers
# docker-compose --profile worker up
```

#### 5. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Worker Dashboard**: http://localhost:5555 (if workers are running)

### Sample Data and Testing

LegalEdge includes comprehensive sample data for development and testing:

```bash
# Seed the database with sample data
cd backend
python -m app.cli seed-sample-data --reset

# Run the test suite
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Load testing
locust -f tests/load/
```

## 📚 Documentation

📚 **Complete Documentation Suite**

### 📖 User Documentation
- **[Getting Started Guide](docs/getting-started/getting-started-guide.md)** - Step-by-step onboarding process
- **[User Guide](docs/user-guide/user-guide.md)** - Comprehensive platform usage guide
- **[Onboarding Guide](docs/onboarding/onboarding-guide.md)** - Detailed 7-phase onboarding process

### 🔧 Developer Documentation
- **[API Documentation](docs/api/api-documentation.md)** - Complete REST API reference
- **[Backend README](backend/README.md)** - Backend development guide
- **[Frontend README](frontend/README.md)** - Frontend development guide
- **[Support Center](docs/support/support-center.md)** - Troubleshooting and support resources

### 💰 Business Documentation
- **[Pricing Guide](docs/pricing/pricing-guide.md)** - Plans, billing, and enterprise options

### 📋 Additional Resources
- **[Disaster Recovery](docs/disaster-recovery.md)** - DR procedures and playbooks
- **[Monitoring Guide](docs/monitoring.md)** - System monitoring and alerting

## 🔌 API Reference

### Core Endpoints

#### Overview & Dashboard
- `GET /api/v1/overview` - Platform overview and feature pillars
- `GET /api/v1/dashboard/snapshot` - Aggregated portfolio and market intelligence

#### Legislation
- `GET /api/v1/legislation/upcoming` - Legislative feed with impact scoring
- `GET /api/v1/legislation/analyze` - Detailed bill analysis and forecasting
- `GET /api/v1/entity-resolution/summary` - Bill-to-ticker mapping coverage

#### Portfolio Intelligence
- `GET /api/v1/portfolios/{id}/analysis` - Portfolio risk and opportunity analysis
- `POST /api/v1/portfolios/{id}/import` - Import holdings via CSV or API
- `GET /api/v1/portfolios/conflicts` - Congressional trade conflict detection

#### Forecasting & Opportunities
- `GET /api/v1/forecasts/sector` - Sector-level market forecasts
- `GET /api/v1/opportunities` - Market opportunity recommendations
- `GET /api/v1/alerts` - Policy and trading alert feed

#### System Health
- `GET /api/v1/health/status` - Application health check
- `GET /api/v1/coverage` - Data coverage and ingestion metrics

## 🔄 Background Processing

LegalEdge uses Celery for robust background task processing:

### Task Categories
- **Ingestion**: Fetch legislative data from multiple sources (every 6 hours)
- **ML Processing**: Retrain models and update forecasts (every 12 hours)
- **Alert Processing**: Process and distribute notifications (every 5 minutes)
- **Data Cleanup**: Archive old data and optimize storage (daily)

### Task Management API
- `GET /api/v1/tasks/status` - Worker queue status
- `POST /api/v1/tasks/ingestion/run` - Trigger manual ingestion
- `GET /api/v1/tasks/models/retrain/legislation` - Retrain ML models

## 🚢 Deployment

### Production Infrastructure

LegalEdge is designed for cloud-native deployment on AWS:

#### Core Services
- **ECS Fargate**: Container orchestration for scalability
- **RDS PostgreSQL**: Primary database with read replicas
- **ElastiCache Redis**: High-performance caching and sessions
- **S3**: Static assets and data lake storage
- **CloudFront**: Global CDN for performance
- **Load Balancer**: Traffic distribution and health checking

#### Infrastructure as Code
```bash
cd infrastructure

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var="environment=production"

# Deploy infrastructure
terraform apply

# Deploy application
docker-compose -f docker-compose.production.yml up -d
```

### Environment Variables

Key configuration variables (see `.env.example` for complete list):

```bash
# Database
LEGALEDGE_DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/legaledge

# Redis
LEGALEDGE_REDIS_URL=redis://host:6379/0

# External APIs
LEGALEDGE_CONGRESS_API_KEY=your_congress_gov_key
LEGALEDGE_NEWS_API_KEY=your_news_api_key

# ML Configuration
LEGALEDGE_ENABLE_TRANSFORMERS=1
LEGALEDGE_MODEL_RETRAIN_SCHEDULE_MINUTES=720

# Monitoring
LEGALEDGE_LOG_LEVEL=INFO
LEGALEDGE_SENTRY_DSN=your_sentry_dsn
```

## 🧪 Testing

Comprehensive test coverage across all components:

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/

# ML model tests
pytest tests/ml/ -m ml

# Performance tests
pytest tests/load/ -m load

# All tests with coverage
pytest --cov=app --cov-report=html
```

## 🔒 Security

Enterprise-grade security measures:

- **Data Encryption**: All data encrypted at rest and in transit
- **Access Control**: Role-based access with JWT authentication
- **Audit Logging**: Complete activity trails for compliance
- **Rate Limiting**: API protection against abuse
- **Input Validation**: Comprehensive sanitization and validation
- **Dependency Scanning**: Automated security vulnerability detection

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the full test suite
6. Submit a pull request

### Development Workflow
```bash
# Set up development environment
git clone <your-fork>
cd LegalEdge

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and run tests
pytest

# Commit and push
git add .
git commit -m "Add amazing feature"
git push origin feature/amazing-feature

# Create pull request
```

## 📊 Monitoring & Observability

### Application Monitoring
- **Health Checks**: Automated health verification endpoints
- **Metrics Collection**: Performance and business metrics
- **Error Tracking**: Centralized error reporting and alerting
- **Log Aggregation**: Structured logging with search capabilities

### Business Intelligence
- **Usage Analytics**: Track feature adoption and user behavior
- **Performance Metrics**: System performance and reliability
- **Custom Dashboards**: Tailored monitoring views

Access monitoring dashboards:
- **Application Metrics**: CloudWatch Dashboard
- **Infrastructure**: AWS Console
- **Logs**: CloudWatch Logs Insights
- **Worker Status**: Flower dashboard at `/flower`

## 🆘 Support

### Getting Help
- **Documentation**: [docs.legaledge.com](https://docs.legaledge.com)
- **Support Center**: [support.legaledge.com](https://support.legaledge.com)
- **Community**: [community.legaledge.com](https://community.legaledge.com)
- **Status Page**: [status.legaledge.com](https://status.legaledge.com)

### Contact Information
- **General Support**: support@legaledge.com
- **Enterprise Sales**: sales@legaledge.com
- **Press Inquiries**: press@legaledge.com
- **Security Issues**: security@legaledge.com

## 📜 License

© 2024 LegalEdge Inc. All rights reserved.

This is proprietary software. See your license agreement for usage terms and restrictions.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- Powered by [React](https://reactjs.org/) - User interface library
- Machine learning with [PyTorch](https://pytorch.org/) and [scikit-learn](https://scikit-learn.org/)
- Deployed on [AWS](https://aws.amazon.com/) with infrastructure as code

---

**Made with ❤️ by the LegalEdge Team**