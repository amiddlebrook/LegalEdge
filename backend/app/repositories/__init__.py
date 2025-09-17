"""Repository helpers for persistence access."""
from app.repositories.forecast import list_sector_forecast
from app.repositories.insights import list_alerts, list_opportunities
from app.repositories.legislation import list_upcoming_legislation
from app.repositories.portfolio import list_recent_trades

__all__ = [
    "list_upcoming_legislation",
    "list_sector_forecast",
    "list_recent_trades",
    "list_alerts",
    "list_opportunities",
]