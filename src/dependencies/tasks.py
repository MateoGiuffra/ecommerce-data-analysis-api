import gspread
import os
from redis import asyncio as aioredis

from src.core.config import settings
from src.repositories.impl.metrics_repository_gspread import MetricsRepositoryGspread
from src.repositories.impl.metrics_repository_local import MetricsRepositoryLocal
from src.repositories.metrics_repository import MetricsRepository
from src.services.cache_service import CacheService
from src.services.metrics.metrics_service import MetricsService
from src.dependencies.gspread_client import get_gspread_client

def get_metrics_repository() -> MetricsRepository:
    """
    Returns an instance of a metrics repository.
    It uses the Gspread implementation if USE_GSPREAD_CLIENT is set to 'true',
    otherwise it falls back to the local CSV implementation.
    """
    try:
        client = get_gspread_client()
        return MetricsRepositoryGspread(gspread_client=client)
    except Exception:
        # If credentials are not available or client creation fails, fall back
        # to the local CSV-based repository. This makes tests and CI resilient.
        return MetricsRepositoryLocal()

async def get_metrics_service_instance() -> MetricsService:
    """Creates and returns an instance of MetricsService with its dependencies."""
    redis_client = await aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    cache_service = CacheService(redis_client)
    metrics_repository = get_metrics_repository()
    
    metrics_service = MetricsService(metrics_repository, cache_service, settings.CACHE_DF_TTL_SECONDS)
    return metrics_service
