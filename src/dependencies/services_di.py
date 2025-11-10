from fastapi import Depends
from src.repositories.impl.user_repository_sql_alchemy import UserRepository
from src.core.config import settings
from redis import asyncio as aioredis
from src.services.user.user_service import UserService
from src.services.user.auth_service import UserAuthService
from src.dependencies.repositories_di import get_user_repository
from src.services.cookie_service import CookieService
from src.services.metrics.product_service import ProductService
from src.services.metrics.customer_service import CustomerService

# ----------------------------------------------------------------------
# CacheService
# ----------------------------------------------------------------------
from src.services.metrics.metrics_service import MetricsService
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

# ----------------------------------------------------------------------
# CookieService
# ----------------------------------------------------------------------

def get_cookie_service() -> CookieService:
    return CookieService()

# ----------------------------------------------------------------------
# UserService
# ----------------------------------------------------------------------

def get_user_service(user_repository: UserRepository = Depends(get_user_repository), cookie_service: CookieService = Depends(get_cookie_service), cache_service: CacheService = Depends(get_cache_service)) -> UserService:
    return UserService(user_repository, cookie_service, cache_service)

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
# UserAuthService
# ----------------------------------------------------------------------

def get_auth_service(user_repository: UserRepository = Depends(get_user_repository), cookie_service: CookieService = Depends(get_cookie_service)):
    return UserAuthService(user_repository, cookie_service)

# ----------------------------------------------------------------------
# MetricsService
# ----------------------------------------------------------------------

def get_metrics_service(metrics_repository: MetricsRepository = Depends(get_metrics_repository), cache_service: CacheService = Depends(get_cache_service)) -> MetricsService:
    return MetricsService(metrics_repository, cache_service, cache_df_ttl_seconds=settings.CACHE_DF_TTL_SECONDS)


# ----------------------------------------------------------------------
# ProductsService
# ----------------------------------------------------------------------
def get_product_service(metrics_repository: MetricsRepository = Depends(get_metrics_repository), cache_service: CacheService = Depends(get_cache_service)) -> ProductService:
    return ProductService(metrics_repository, cache_service, cache_df_ttl_seconds=settings.CACHE_DF_TTL_SECONDS)

# ----------------------------------------------------------------------
# CustomerService
# ----------------------------------------------------------------------
def get_customer_service(metrics_repository: MetricsRepository = Depends(get_metrics_repository), cache_service: CacheService = Depends(get_cache_service)) -> CustomerService:
    return CustomerService(metrics_repository, cache_service, cache_df_ttl_seconds=settings.CACHE_DF_TTL_SECONDS)

#