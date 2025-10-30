from redis.asyncio import Redis
import pandas as pd
from pandas import DataFrame
from typing import Optional, Callable, Any, Type
import logging
from functools import wraps
from src.core.config import settings
from io import StringIO
import inspect
import json
import typing
from pydantic import BaseModel, create_model
from sqlalchemy.orm import DeclarativeMeta
logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.ttl = settings.CACHE_TTL_SECONDS

    async def get_dataframe(self, key: str) -> Optional[DataFrame]:
        """
        Retrieves and deserializes a pandas DataFrame from the cache.
        """
        cached_df_json = await self.redis_client.get(key)
        if cached_df_json:
            logger.info(f"Cache HIT for key: {key}")
            return pd.read_json(StringIO(cached_df_json), orient='split')
        logger.info(f"Cache MISS for key: {key}")
        return None


    async def set_dataframe(self, key: str, df: DataFrame, ttl_seconds: int) -> None:
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
            logger.info("executing cache_dataframe")
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cached_df = await self.get_dataframe(key)
                if cached_df is not None:
                    return cached_df
                
                new_df = await func(*args, **kwargs)
                await self.set_dataframe(key, new_df, ttl_seconds)
                return new_df
            
            return wrapper
        
        return decorator

    def cache(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator to cache the result of a generic async function.
        The result must be JSON serializable.
        """
        @wraps(func)
        async def wrapper(instance, *args, **kwargs):
            logger.info("executing cache")
            key: str = self.generate_key(func, instance, *args, **kwargs)
            try:
                cached_value = await self.redis_client.get(key)
                if cached_value is not None:
                    logger.info(f"Cache HIT for generic key: {key}")
                    data = json.loads(cached_value)
                    return_type = inspect.signature(func).return_annotation

                    if return_type is inspect.Signature.empty:
                        logger.warning(f"Cache deserialization skipped for '{func.__qualname__}': Missing return type. Returning raw dict.")
                        return data

                    return self._deserialize_data(data, return_type)
            except Exception as e:
                logger.error(f"Cache GET error for key {key}: {e}")

            logger.info(f"Cache MISS for generic key: {key}")
            result = await func(instance, *args, **kwargs)
            await self.set_cache(key, result)
            return result
        return wrapper
    
    def _deserialize_data(self, data: Any, return_type: Type) -> Any:
        """Recursively deserializes data into the specified Pydantic or SQLAlchemy model type."""
        origin = typing.get_origin(return_type)

        if origin in (list, typing.List) and isinstance(data, list):
            item_type = typing.get_args(return_type)[0]
            return [self._deserialize_data(item, item_type) for item in data]

        if inspect.isclass(return_type) and issubclass(return_type, BaseModel):
            return return_type.model_validate(data)
        
        if isinstance(return_type, DeclarativeMeta): # It's a SQLAlchemy model class
            return return_type(**data)

        return data # Fallback for simple types

    def generate_key(self, func: Callable[..., Any], instance: Any, *args: Any, **kwargs: Any) -> str:
        """
        Generates a robust cache key based on the function's qualified name
        and a representation of its arguments.
        """
        func_name = func.__qualname__
        # Use repr() for a stable representation of basic types. Avoids complex object string conversion.
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={repr(v)}" for k, v in sorted(kwargs.items())]
        return f"{func_name}:{':'.join(args_repr + kwargs_repr)}"
    
    async def set_cache(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Serializes and stores a value in the cache with a TTL."""
        if ttl_seconds is None:
            ttl_seconds = self.ttl
        
        serialized_value = self._serialize_value(value)
        await self.redis_client.set(key, serialized_value, ex=ttl_seconds)

    def _serialize_value(self, value: Any) -> str:
        """Recursively serializes a value to a JSON string."""
        if isinstance(value, (list, tuple)):
            # Correctly handle lists by serializing each item and then the whole list.
            # We need to load the inner serialized string back to an object before the final dump.
            processed_items = [json.loads(self._serialize_value(item)) for item in value]
            return json.dumps(processed_items)

        if isinstance(value, BaseModel): # It's a Pydantic model
            # Serialize Pydantic models by recursively serializing their fields
            # This correctly handles nested SQLAlchemy models inside Pydantic models.
            obj_dict = {field: json.loads(self._serialize_value(getattr(value, field))) for field in value.model_fields}
            return json.dumps(obj_dict)

        if hasattr(value, '_sa_instance_state'): # It's a SQLAlchemy instance
            # Dynamically create a Pydantic model from the SQLAlchemy model
            # This allows using .model_dump() for clean serialization
            pydantic_model = create_model(
                f'{value.__class__.__name__}Pydantic',
                **{c.name: (c.type.python_type, ...) for c in value.__table__.columns}
            )
            return pydantic_model.model_validate(value, from_attributes=True).model_dump_json()
        
        return json.dumps(value) # Fallback for simple types
        
    async def delete_cache(self) -> None:
        """
        Deletes the cache.
        """
        await self.redis_client.flushdb()