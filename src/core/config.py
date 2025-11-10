from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="ignore")

    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    COOKIE_SECURE: bool = False
    DEFAULT_PUBLIC_PATHS: set = {"/", "/docs", "/openapi.json"}
    # When True the app is running in test mode; some validations may be relaxed
    TESTING: bool = False
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./app.db"

    # Google / spreadsheet settings — optional to make CI/tests easier.
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = ""
    GOOGLE_PROJECT_ID: Optional[str] = ""
    GOOGLE_PRIVATE_KEY_ID: Optional[str] = ""
    GOOGLE_PRIVATE_KEY: Optional[str] = ""
    GOOGLE_CLIENT_EMAIL: Optional[str] = ""
    SPREADSHEET_ID: Optional[str] = ""
    SPREADSHEET_GID: Optional[str] = ""
    API_KEY: Optional[str] = ""
    TOKEN_URI: Optional[str] = ""

    # cache
    CACHE_TTL_SECONDS: int = 300
    CACHE_DF_TTL_SECONDS: int = 600
    REDIS_URL: str = "redis://localhost:6379/0"
    # celery
    CELERY_BROKER_URL: str = 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND: str = 'redis://localhost:6379/1'


settings = Settings()
