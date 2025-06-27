"""
Health check endpoints.
"""

from datetime import datetime
from fastapi import APIRouter
from loguru import logger

from src.data.models import HealthCheck
from src.config.settings import settings

router = APIRouter()


@router.get("/", response_model=HealthCheck)
async def health_check():
    """
    Basic health check endpoint.
    """
    try:
        # Check database connectivity (implement actual check)
        db_status = "healthy"
        
        # Check AI services (implement actual check)
        ai_status = "healthy"
        
        # Check vector database (implement actual check)
        vector_db_status = "healthy"
        
        dependencies = {
            "database": db_status,
            "ai_service": ai_status,
            "vector_db": vector_db_status
        }
        
        return HealthCheck(
            status="healthy",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            dependencies=dependencies
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheck(
            status="unhealthy",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            dependencies={"error": str(e)}
        )


@router.get("/detailed")
async def detailed_health_check():
    """
    Detailed health check with component status.
    """
    try:
        checks = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": {
                "debug": settings.DEBUG,
                "log_level": settings.LOG_LEVEL
            },
            "components": {
                "api": "healthy",
                "database": "healthy",  # Implement actual check
                "ai_service": "healthy",  # Implement actual check
                "vector_database": "healthy",  # Implement actual check
                "logging": "healthy"
            }
        }
        
        return checks
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
