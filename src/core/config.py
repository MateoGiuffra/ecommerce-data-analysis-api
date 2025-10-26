from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="ignore")

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    COOKIE_SECURE: bool = False
    DEFAULT_PUBLIC_PATHS: set = {"/", "/docs", "/openapi.json"}
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./app.db"
    GOOGLE_APPLICATION_CREDENTIALS: str
    GOOGLE_PROJECT_ID: str
    GOOGLE_PRIVATE_KEY_ID: str
    GOOGLE_PRIVATE_KEY: str
    GOOGLE_CLIENT_EMAIL: str
    SPREADSHEET_ID: str
    SPREADSHEET_GID: str
    API_KEY: str
    TOKEN_URI: str

settings = Settings()
