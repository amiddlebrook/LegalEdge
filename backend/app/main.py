"""FastAPI application factory."""
from contextlib import asynccontextmanager
from functools import partial
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.tasks import RecurringTaskManager
from app.db.session import SessionLocal
from app.workflows.pipeline import retrain_legislation_models, run_daily_ingestion


def create_application() -> FastAPI:
    """Configure and return the FastAPI app instance."""

    configure_logging()

    ingestion_job = partial(run_daily_ingestion, session_factory=SessionLocal)
    ingestion_manager = RecurringTaskManager(
        ingestion_job,
        interval_minutes=settings.ingestion_schedule_minutes,
        run_immediately=True,
    )
    retraining_manager = RecurringTaskManager(
        retrain_legislation_models,
        interval_minutes=settings.model_retrain_schedule_minutes,
        run_immediately=False,
    )
    managers = [ingestion_manager, retraining_manager]

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if settings.environment.lower() != "test":
            for manager in managers:
                await manager.start()
        try:
            yield
        finally:
            if settings.environment.lower() != "test":
                for manager in reversed(managers):
                    await manager.stop()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Allow local dev and future UI origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_application()
