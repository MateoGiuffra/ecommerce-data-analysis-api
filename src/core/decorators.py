from typing import Callable

def public(func: Callable) -> Callable:
    setattr(func, "_is_public", True)
    return func

