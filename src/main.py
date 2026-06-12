import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.core.config import get_settings
from src.core.logger import setup_logging

settings = get_settings()

# Initialize unified logging configuration
setup_logging()
logger = logging.getLogger("asset-link")


# Manage application lifecycle
@asynccontextmanager
async def lifespan_context(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Application startup initiated.")
    yield
    logger.info("Application shutdown initiated.")


app = FastAPI(
    title="Asset Link API Server",
    version="0.1.0",
    debug=settings.IS_DEBUG,
    lifespan=lifespan_context, # type: ignore
)


@app.get("/health", status_code=200)
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "environment": "debug" if settings.IS_DEBUG else "production"}