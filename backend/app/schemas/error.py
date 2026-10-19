"""Schema representing structured error response."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standardized API error response format."""

    error: str = Field(description="High-level error classification or message")
    detail: Optional[str] = Field(default=None, description="Detailed explanation of the error")
    code: str = Field(default="INTERNAL_ERROR", description="Machine-readable error code")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional context if safe to expose")
