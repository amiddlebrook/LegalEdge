"""Version 1 API router."""
from fastapi import APIRouter

from . import routes_alerts, routes_dashboard, routes_forecasts, routes_health, routes_legislation, routes_opportunities, routes_portfolios, routes_overview


router = APIRouter()
router.include_router(routes_health.router)
router.include_router(routes_legislation.router)
router.include_router(routes_forecasts.router)
router.include_router(routes_portfolios.router)
router.include_router(routes_overview.router)
router.include_router(routes_dashboard.router)
router.include_router(routes_opportunities.router)
router.include_router(routes_alerts.router)
