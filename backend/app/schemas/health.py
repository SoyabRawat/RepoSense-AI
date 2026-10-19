"""Schema representing structured health check response."""

from datetime import datetime, timezone
from typing import Dict, Literal
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Structured health check response model."""

    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        default="healthy",
        description="Current status of the backend API service",
    )
    app_name: str = Field(
        default="RepoSense AI Backend",
        description="Name of the running application",
    )
    version: str = Field(
        default="0.2.0-alpha.2",
        description="Semantic version of the application",
    )
    phase: str = Field(
        default="Phase 2 - Core Development",
        description="Current project development phase",
    )
    environment: str = Field(
        default="development",
        description="Execution environment (development, test, production)",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the health check was performed",
    )
    capabilities: Dict[str, str] = Field(
        default_factory=lambda: {
            "health_check": "active",
            "repository_ingestion": "active",
            "ast_parsing": "active",
            "graph_visualization": "active",
            "source_code_search": "active",
            "ai_explanations": "active",
        },
        description="Explicit declaration of capability readiness to prevent false assumptions",
    )
