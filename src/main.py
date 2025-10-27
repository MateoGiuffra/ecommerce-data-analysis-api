from fastapi import FastAPI
from src.routers import routers
from fastapi.routing import APIRoute
from src.handlers import exception_handlers
from src.core.middleware import JWTCookieAuthMiddleware
from src.core.config import settings
from src.core.logging_config import setup_logging
from contextlib import asynccontextmanager
from src.dependencies.services_di import get_redis_client

setup_logging()

app = FastAPI(
    description="API REST",
    version="1.0.1",
    exception_handlers=exception_handlers,
)

def set_up(app: FastAPI):
    public_paths = set(settings.DEFAULT_PUBLIC_PATHS)
    for router in routers:
        app.include_router(router)
    for route in app.routes:
        if isinstance(route, APIRoute):
            if getattr(route.endpoint, "_is_public", False):
                public_paths.add(route.path)
    
    app.add_middleware(JWTCookieAuthMiddleware, public_paths=public_paths)

set_up(app)
