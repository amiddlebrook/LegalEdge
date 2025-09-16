"""Version 1 API router."""
from fastapi import APIRouter

from . import routes_forecasts, routes_health, routes_legislation, routes_portfolios


router = APIRouter()
router.include_router(routes_health.router)
router.include_router(routes_legislation.router)
router.include_router(routes_forecasts.router)
router.include_router(routes_portfolios.router)