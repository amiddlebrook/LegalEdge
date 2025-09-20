"""Version 1 API router."""
from fastapi import APIRouter

from . import (
    routes_alerts,
    routes_auth,
    routes_coverage,
    routes_dashboard,
    routes_entity_resolution,
    routes_forecasts,
    routes_health,
    routes_legislation,
    routes_opportunities,
    routes_portfolios,
    routes_overview,
    routes_tasks,
)


router = APIRouter()
router.include_router(routes_health.router)
router.include_router(routes_coverage.router)
router.include_router(routes_legislation.router)
router.include_router(routes_forecasts.router)
router.include_router(routes_portfolios.router)
router.include_router(routes_overview.router)
router.include_router(routes_dashboard.router)
router.include_router(routes_opportunities.router)
router.include_router(routes_alerts.router)
router.include_router(routes_entity_resolution.router)
router.include_router(routes_auth.router)
router.include_router(routes_tasks.router)
