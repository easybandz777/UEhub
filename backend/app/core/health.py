"""
Health check endpoints and utilities.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .container import get_cache_service, get_container
from .db import get_db
from .interfaces import CacheService
from .settings import get_settings

settings = get_settings()
router = APIRouter()


class HealthStatus(BaseModel):
    """Health check status."""
    status: str
    timestamp: datetime
    version: str
    environment: str


class ServiceHealth(BaseModel):
    """Individual service health."""
    name: str
    status: str
    response_time_ms: Optional[float] = None
    error: Optional[str] = None


class DetailedHealthStatus(BaseModel):
    """Detailed health check with service statuses."""
    status: str
    timestamp: datetime
    version: str
    environment: str
    services: List[ServiceHealth]


async def check_database_health(db: AsyncSession) -> ServiceHealth:
    """Check database connectivity."""
    start_time = datetime.now()
    
    try:
        # Simple query to test connection
        result = await db.execute(text("SELECT 1"))
        result.fetchone()
        
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        return ServiceHealth(
            name="database",
            status="healthy",
            response_time_ms=response_time
        )
    
    except Exception as e:
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        return ServiceHealth(
            name="database",
            status="unhealthy",
            response_time_ms=response_time,
            error=str(e)
        )


async def check_cache_health(cache: CacheService) -> ServiceHealth:
    """Check cache connectivity."""
    start_time = datetime.now()
    
    try:
        # Test cache with a simple operation
        test_key = "health_check"
        test_value = "ok"
        
        await cache.set(test_key, test_value, ttl=10)
        result = await cache.get(test_key)
        
        if result != test_value:
            raise Exception("Cache read/write test failed")
        
        await cache.delete(test_key)
        
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        return ServiceHealth(
            name="cache",
            status="healthy",
            response_time_ms=response_time
        )
    
    except Exception as e:
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        return ServiceHealth(
            name="cache",
            status="unhealthy",
            response_time_ms=response_time,
            error=str(e)
        )


async def check_event_bus_health() -> ServiceHealth:
    """Check event bus health."""
    start_time = datetime.now()
    
    try:
        container = get_container()
        event_bus = container.event_bus
        
        # For in-process event bus, just check if it exists
        # For Redis event bus, we could do a more thorough check
        if event_bus:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return ServiceHealth(
                name="event_bus",
                status="healthy",
                response_time_ms=response_time
            )
        else:
            raise Exception("Event bus not initialized")
    
    except Exception as e:
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        return ServiceHealth(
            name="event_bus",
            status="unhealthy",
            response_time_ms=response_time,
            error=str(e)
        )


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """Basic health check endpoint."""
    return HealthStatus(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.app.version,
        environment=settings.app.environment
    )


@router.get("/health/detailed", response_model=DetailedHealthStatus)
async def detailed_health_check(
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache_service)
):
    """Detailed health check with service statuses."""
    
    # Run health checks concurrently
    health_checks = await asyncio.gather(
        check_database_health(db),
        check_cache_health(cache),
        check_event_bus_health(),
        return_exceptions=True
    )
    
    services = []
    overall_status = "healthy"
    
    for check_result in health_checks:
        if isinstance(check_result, Exception):
            services.append(ServiceHealth(
                name="unknown",
                status="unhealthy",
                error=str(check_result)
            ))
            overall_status = "unhealthy"
        else:
            services.append(check_result)
            if check_result.status != "healthy":
                overall_status = "unhealthy"
    
    return DetailedHealthStatus(
        status=overall_status,
        timestamp=datetime.now(),
        version=settings.app.version,
        environment=settings.app.environment,
        services=services
    )


@router.get("/health/readiness")
async def readiness_check(
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache_service)
):
    """Kubernetes readiness probe endpoint."""
    
    try:
        # Check critical services
        db_health = await check_database_health(db)
        cache_health = await check_cache_health(cache)
        
        if db_health.status != "healthy" or cache_health.status != "healthy":
            return {"status": "not_ready"}, 503
        
        return {"status": "ready"}
    
    except Exception:
        return {"status": "not_ready"}, 503


@router.get("/health/liveness")
async def liveness_check():
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive"}
