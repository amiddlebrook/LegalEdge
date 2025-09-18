# LegalEdge Completion Roadmap

This document tracks outstanding work required to ship the LegalEdge platform as outlined in the product brief. Update it as tasks are completed or new needs emerge.

## Legislative & Data Ingestion
- [x] Build connectors for congress.gov, state portals, SEC Form 4/13D, and news/RSS feeds with resilient polling and rate limiting.
- [x] Normalize, deduplicate, and version legislative artifacts in PostgreSQL with jurisdiction coverage metrics.
- [x] Implement entity resolution linking bills to tickers, committees, sectors, and maintain data quality dashboards.

## AI & Market Intelligence
- [x] Deliver transformer-based NLP pipeline for bill sentiment, enactment probability, and sector impact scoring; automate retraining (hybrid pipeline with scheduled recalibration).
- [x] Develop time-series forecasting engine that blends policy signals with market data to reach the 70%+ accuracy target (hybrid policy + momentum model with scheduled retraining).
- [x] Operationalize market opportunity ranking and conflict scoring using live data plus ML outputs with explainability (policy-aware ranker + conflict dampening in API).

## Portfolio & Alerts Experience
- [ ] Continuously ingest and normalize congressional trade disclosures, linking trades to pending legislation.
- [ ] Implement configurable alerting (severity, category, personalization) with push channels (email/SMS/webhooks).
- [x] Expand portfolio dashboards with drilldowns (member history, bill timelines, watchlists) and exportable reports.

## Backend Platform
- [ ] Replace stub repositories with full SQLAlchemy models, migrations, CRUD, and caching layers.
- [ ] Add OAuth 2.0 authentication, role-based access, rate limiting, audit logging, and polished OpenAPI documentation.
- [ ] Stand up background workers (Celery/Prefect) for ingestion, enrichment, retraining, and scheduled snapshots.

## Frontend Experience
- [ ] Enrich dashboard with live charts/visualizations, coverage heatmaps, and legislation timelines.
- [ ] Build alert management UI, portfolio conflict explorer, and persona-specific workflows.
- [ ] Implement global state/query caching, skeleton loading states, responsive polish, and accessibility compliance.

## Infrastructure & Operations
- [ ] Provision AWS infrastructure (VPC, ECS/Lambda, RDS, S3, CloudFront) via Terraform with automated deploys.
- [ ] Configure CI/CD with tests, linting, security scans, and observability (metrics, tracing, logging).
- [ ] Establish disaster recovery playbooks, data retention policies, and cost monitoring.

## Security & Compliance
- [ ] Enforce encryption at rest/in transit, secrets rotation, vulnerability scanning, and dependency governance.
- [ ] Implement SOC2-aligned controls: change management, access reviews, incident response, and logging.
- [ ] Build privacy/compliance tooling for jurisdictional regulations and client data segregation.

## Quality & Go-To-Market Readiness
- [ ] Expand automated tests (unit/integration/e2e), load tests for ingestion/alerts, and ML evaluation harnesses.
- [ ] Produce client-facing documentation, onboarding flows, pricing/billing integration, and support playbooks.
- [ ] Add feedback loops (in-app telemetry, surveys) and plan iterative release cadence post-launch.


