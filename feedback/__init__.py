"""Integration layer for feedback and analytics system."""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from typing import Optional, Dict, Any
import logging

from app.core.auth import get_current_user
from .feedback_service import feedback_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.get("/analytics/dashboard")
async def get_analytics_dashboard(current_user: dict = Depends(get_current_user)):
    """Get analytics dashboard for the current user."""
    try:
        return await feedback_service.get_analytics_dashboard(current_user.get("id"))
    except Exception as e:
        logger.error(f"Error getting analytics dashboard: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analytics")


@router.get("/surveys")
async def get_available_surveys(request: Request, current_user: dict = Depends(get_current_user)):
    """Get available surveys for the current user."""
    try:
        session_id = request.cookies.get("session_id", "unknown")
        surveys = await feedback_service.get_user_surveys(current_user.get("id"), session_id)
        return {"surveys": surveys}
    except Exception as e:
        logger.error(f"Error getting surveys: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving surveys")


@router.post("/surveys/{survey_id}/respond")
async def submit_survey_response(
    survey_id: str,
    response_data: Dict[str, Any],
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Submit a survey response."""
    try:
        session_id = request.cookies.get("session_id", "unknown")
        success = await feedback_service.submit_survey_response(
            survey_id,
            current_user.get("id"),
            session_id,
            response_data.get("responses", {})
        )

        if success:
            return {"message": "Survey response submitted successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to submit survey response")

    except Exception as e:
        logger.error(f"Error submitting survey response: {e}")
        raise HTTPException(status_code=500, detail="Error submitting survey response")


@router.post("/feature-requests")
async def create_feature_request(
    request_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Create a feature request."""
    try:
        feature = await feedback_service.create_feature_request(
            request_data,
            current_user.get("id")
        )
        return {"feature": feature, "message": "Feature request submitted successfully"}
    except Exception as e:
        logger.error(f"Error creating feature request: {e}")
        raise HTTPException(status_code=500, detail="Error creating feature request")


@router.get("/system/health")
async def get_system_health():
    """Get system health status."""
    try:
        return await feedback_service.get_system_health()
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving system health")


@router.get("/insights")
async def get_insights_report(current_user: dict = Depends(get_current_user)):
    """Get comprehensive insights report."""
    try:
        return await feedback_service.generate_insights_report()
    except Exception as e:
        logger.error(f"Error generating insights report: {e}")
        raise HTTPException(status_code=500, detail="Error generating insights")


# Telemetry tracking endpoints (typically called from frontend)
@router.post("/track")
async def track_event(
    event_data: Dict[str, Any],
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Track a user event for analytics."""
    try:
        await feedback_service.track_user_event(
            event_type=event_data.get("event_type"),
            user_id=current_user.get("id"),
            session_id=request.cookies.get("session_id"),
            event_data=event_data.get("event_data", {})
        )
        return {"status": "tracked"}
    except Exception as e:
        logger.error(f"Error tracking event: {e}")
        # Don't raise exception for tracking failures to avoid disrupting user experience
        return {"status": "error", "message": str(e)}


# A/B Testing endpoints
@router.get("/experiments/{test_id}/variant")
async def get_ab_test_variant(
    test_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get A/B test variant for user."""
    try:
        variant_id = await feedback_service.get_ab_test_variant(test_id, current_user.get("id"))
        if variant_id:
            return {"test_id": test_id, "variant_id": variant_id}
        else:
            raise HTTPException(status_code=404, detail="Test not found or not available")
    except Exception as e:
        logger.error(f"Error getting A/B test variant: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving test variant")


@router.post("/experiments/{test_id}/events")
async def track_ab_test_event(
    test_id: str,
    event_data: Dict[str, Any],
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Track an A/B test event."""
    try:
        await feedback_service.track_ab_test_event(
            test_id,
            current_user.get("id"),
            event_data.get("event_name"),
            event_data.get("event_data", {})
        )
        return {"status": "tracked"}
    except Exception as e:
        logger.error(f"Error tracking A/B test event: {e}")
        return {"status": "error", "message": str(e)}


# Admin endpoints for managing feedback system
@router.post("/admin/initialize")
async def initialize_feedback_system(current_user: dict = Depends(get_current_user)):
    """Initialize the feedback system (admin only)."""
    try:
        # Check if user is admin
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")

        await feedback_service.initialize_system()
        return {"message": "Feedback system initialized successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing feedback system: {e}")
        raise HTTPException(status_code=500, detail="Error initializing feedback system")


@router.get("/admin/analytics/summary")
async def get_analytics_summary(
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """Get analytics summary (admin only)."""
    try:
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")

        from .telemetry_service import TelemetryService
        summary = await TelemetryService.get_analytics_summary(days)
        return {"summary": summary}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analytics summary")


@router.get("/admin/surveys/results/{survey_id}")
async def get_survey_results(
    survey_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get survey results (admin only)."""
    try:
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")

        from .survey_service import SurveyService
        results = await SurveyService.get_survey_results(survey_id)
        return {"results": results}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting survey results: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving survey results")


@router.get("/admin/experiments/results/{test_id}")
async def get_ab_test_results(
    test_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get A/B test results (admin only)."""
    try:
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")

        from .ab_testing_service import ABTestService
        results = await ABTestService.get_test_results(test_id)
        return {"results": results}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting A/B test results: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving test results")


# Middleware for automatic telemetry tracking
class TelemetryMiddleware:
    """Middleware for automatic telemetry tracking."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract request information
        request = Request(scope, receive)
        start_time = datetime.now()

        # Process request
        response = await self.app(scope, receive, send)

        # Track page view if GET request
        if scope["method"] == "GET":
            # Extract user ID from headers or session
            user_id = getattr(request.state, "user_id", None)

            # Track page view
            await feedback_service.track_user_event(
                "page_view",
                user_id=user_id,
                event_data={
                    "page_url": str(request.url),
                    "user_agent": request.headers.get("user-agent", ""),
                    "ip_address": request.client.host if request.client else None
                }
            )

        return response


# Utility functions for easy integration
def track_page_view(user_id: Optional[str], page_url: str):
    """Track a page view event."""
    asyncio.create_task(feedback_service.track_user_event(
        "page_view",
        user_id=user_id,
        event_data={"page_url": page_url}
    ))


def track_feature_use(user_id: Optional[str], feature_name: str):
    """Track feature usage."""
    asyncio.create_task(feedback_service.track_user_event(
        "feature_use",
        user_id=user_id,
        event_data={"feature_name": feature_name}
    ))


def track_error(user_id: Optional[str], error_message: str, error_context: Optional[Dict] = None):
    """Track an error event."""
    asyncio.create_task(feedback_service.track_user_event(
        "error",
        user_id=user_id,
        event_data={
            "message": error_message,
            "context": error_context or {}
        }
    ))


# Export all components for easy access
__all__ = [
    "feedback_service",
    "track_page_view",
    "track_feature_use",
    "track_error",
    "router",
    "TelemetryMiddleware"
]
