from fastapi import Depends
from src.repositories.impl.user_repository_sql_alchemy import UserRepository
from src.core.config import settings
from redis import asyncio as aioredis
from src.services.user_service import UserService
from src.dependencies.repositories_di import get_user_repository
from src.services.cookie_service import CookieService

def get_cookie_service() -> CookieService:
    return CookieService()

def get_user_service(user_repository: UserRepository = Depends(get_user_repository), cookie_service: CookieService = Depends(get_cookie_service)) -> UserService:
    return UserService(user_repository, cookie_service)


# Shorthand
def get_injected_user_service(
    user_service: UserService = Depends(get_user_service)
) -> UserService:
    """
    Dependencia auxiliar para acceder al UserService. 
    Se usa en el router como atajo (shorthand) para evitar repetir Depends(...) 
    en la declaración de la variable UserServiceDep.
    """
    return user_service

# ----------------------------------------------------------------------
# MetricsService
# ----------------------------------------------------------------------
from src.services.metrics_service import MetricsService
from src.dependencies.repositories_di import get_metrics_repository
from src.services.cache_service import CacheService
from src.repositories.metrics_repository import MetricsRepository


async def get_redis_client():
    redis = await aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    try:
        yield redis
    finally:
        await redis.close()

def get_cache_service(redis_client: aioredis.Redis = Depends(get_redis_client)) -> CacheService:
    return CacheService(redis_client)

def get_metrics_service(metrics_repository: MetricsRepository = Depends(get_metrics_repository), cache_service: CacheService = Depends(get_cache_service)) -> MetricsService:
    return MetricsService(metrics_repository, cache_service, cache_ttl_seconds=settings.CACHE_TTL_SECONDS)