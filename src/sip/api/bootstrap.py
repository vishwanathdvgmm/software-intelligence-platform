"""FastAPI application bootstrap and lifecycle management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
import structlog

from sip.core.config import get_settings
from sip.core.container import ApplicationContainer

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle."""
    logger.info("app.lifespan.startup", msg="Starting SIP Core API")
    
    try:
        settings = get_settings()
        container = ApplicationContainer(settings)
        await container.start()
        
        # Attach to app state for dependencies to consume
        app.state.container = container
        
        yield
    except Exception as e:
        logger.exception("app.lifespan.startup_failed", msg="Failed to start application", error=str(e))
        raise
    finally:
        logger.info("app.lifespan.shutdown", msg="Shutting down SIP Core API")
        if hasattr(app.state, "container") and app.state.container:
            await app.state.container.stop()
        logger.info("app.lifespan.shutdown_complete", msg="Shutdown complete")
