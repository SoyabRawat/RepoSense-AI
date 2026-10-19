"""Pydantic schemas for API request and response data structures."""

from app.schemas.health import HealthResponse
from app.schemas.error import ErrorResponse

__all__ = ["HealthResponse", "ErrorResponse"]
