from typing import Callable

def public(func: Callable) -> Callable:
    setattr(func, "_is_public", True)
    return func

def non_cacheable(func: Callable) -> Callable:
    setattr(func, "_is_non_cacheable", True)
    return func 

def excluded_from_cache(func: Callable) -> Callable:
    setattr(func, "_is_excluded_from_cache", True)
    return func
