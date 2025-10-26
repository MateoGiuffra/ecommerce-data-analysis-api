from redis.asyncio import Redis
import pandas as pd
from pandas import DataFrame
from typing import Optional, Callable, Any
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def get_dataframe(self, key: str) -> Optional[DataFrame]:
        """
        Retrieves and deserializes a pandas DataFrame from the cache.
        """
        cached_df_json = await self.redis_client.get(key)
        if cached_df_json:
            logger.info(f"Cache HIT for key: {key}")
            return pd.read_json(cached_df_json, orient='split')
        logger.info(f"Cache MISS for key: {key}")
        return None

    async def set_dataframe(self, key: str, df: DataFrame, ttl_seconds: int):
        """
        Serializes and stores a pandas DataFrame in the cache with a TTL.
        """
        df_json = df.to_json(orient='split')
        await self.redis_client.set(key, df_json, ex=ttl_seconds)
        logger.info(f"Cache SET for key: {key} with TTL: {ttl_seconds}s")

    def cache_dataframe(self, key: str, ttl_seconds: int):
        """
        Decorator to cache the result of a function that returns a pandas DataFrame.
        """
        def decorator(func: Callable[..., Any]):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 'self' in 'wrapper' refers to the instance of the class
                # where the decorated method is defined (e.g., MetricsService instance).
                # We need the CacheService instance, which is available in the
                # scope of the 'decorator' function. Let's call it 'cache_self'.
                cache_self = self

                # 1. Try to get from cache
                cached_df = await cache_self.get_dataframe(key)
                if cached_df is not None:
                    return cached_df

                # 2. If miss, execute the original function
                new_df = await func(*args, **kwargs)

                # 3. Store the new result in cache
                await cache_self.set_dataframe(key, new_df, ttl_seconds)
                return new_df
            return wrapper
        return decorator