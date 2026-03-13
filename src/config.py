from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    openai_api_key: str
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    database_url: str = "sqlite:///./pmcursor.db"
    upload_dir: str = "uploads"
    data_dir: str = "data"
    max_upload_size_mb: int = 50

    model_config = {"env_file": ".env"}


settings = Settings()
