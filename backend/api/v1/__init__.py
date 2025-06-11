"""API v1 routes"""

from fastapi import APIRouter
from .events import router as events_router
from .auth import router as auth_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include sub-routers
api_router.include_router(auth_router)
api_router.include_router(events_router)

__all__ = ['api_router']