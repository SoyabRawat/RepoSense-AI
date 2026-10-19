"""FastAPI application entry point for RepoSense AI."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.api.v1.endpoints import health
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.schemas.error import ErrorResponse

logger = logging.getLogger("reposense.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for startup and shutdown routines."""
    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info("Starting %s in [%s] mode (%s)", settings.app_name, settings.app_env, settings.phase)
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_application() -> FastAPI:
    """Factory function to build and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="RepoSense AI - Developer tool for understanding unfamiliar codebases.",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # Configure CORS for local frontend communication
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # Top-level direct health check for convenience
    app.include_router(health.router)

    # API v1 routes
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # Custom exception handlers for consistent responses
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail_msg = exc.detail if isinstance(exc.detail, str) else "HTTP Exception"
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=detail_msg,
                detail=detail_msg,
                code=f"HTTP_{exc.status_code}",
                metadata={"path": str(request.url.path)},
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        status_code = getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422)
        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(
                error="Input validation failed",
                detail=str(exc.errors()),
                code="VALIDATION_ERROR",
                metadata={"path": str(request.url.path)},
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled server exception: %s", str(exc), exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="An unexpected internal error occurred",
                code="INTERNAL_SERVER_ERROR",
                metadata={"path": str(request.url.path)},
            ).model_dump(),
        )

    return app


app = create_application()
