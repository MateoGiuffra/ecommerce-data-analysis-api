from functools import wraps
import inspect

class Caching(type):
    def __new__(mcs: type, name: str, bases: tuple, attrs: dict):
        for attr_name, attr_value in attrs.items():
            if mcs._is_cacheable_method(attr_name, attr_value):
                attrs[attr_name] = mcs._create_cached_wrapper(attr_value)
        return super().__new__(mcs, name, bases, attrs)

    @staticmethod
    def _is_cacheable_method(attr_name: str, attr_value) -> bool:
        """Checks if a method should be cached."""
        return inspect.iscoroutinefunction(attr_value) and \
               not attr_name.startswith("_") and \
               not getattr(attr_value, "_is_excluded_from_cache", False)

    @staticmethod
    def _create_cached_wrapper(original_method):
        """Creates a wrapper that applies caching using the instance's cache_service."""
        @wraps(original_method)
        async def _cached_method_wrapper(self, *args, **kwargs):
            if not hasattr(self, 'cache_service'):
                # Failsafe: if the instance doesn't have a cache_service, just run the original method.
                return await original_method(self, *args, **kwargs)
            
            # The actual caching logic is now delegated to the cache_service's `cache` method.
            return await self.cache_service.cache(original_method)(self, *args, **kwargs)
        return _cached_method_wrapper