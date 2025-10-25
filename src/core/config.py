from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="ignore")

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    COOKIE_SECURE: bool = False
    DEFAULT_PUBLIC_PATHS: set = {"/", "/docs", "/openapi.json"}
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./app.db"

settings = Settings()
