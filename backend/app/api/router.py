"""Central API router configuration."""

from fastapi import APIRouter
from app.api.v1.endpoints import health, repositories

api_router = APIRouter()

# Include version 1 endpoint modules
api_router.include_router(health.router)
api_router.include_router(repositories.router)
