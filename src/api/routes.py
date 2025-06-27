"""
API routes for the GenAI Email Processing System.
"""

from fastapi import APIRouter
from src.api.endpoints import emails, search, health

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(emails.router, prefix="/emails", tags=["emails"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
