"""Configuration settings for the application."""

import logging
import sys

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "church_management"
    test_database_name: str = "church_management_test"
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    refresh_token_expire_days: int = 30  # 30 days
    gemini_api_key: str = ""
    ai_service: str = "local"  # gemini | local
    local_ai_url: str = "http://localhost:1234"
    local_ai_model: str = "local-model"
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    model_config = ConfigDict(env_file=".env", extra="ignore")


def setup_logging():
    """Setup logging configuration."""
    app_settings = Settings()

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, app_settings.log_level.upper()),
        format=app_settings.log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log", mode="a"),
        ],
    )

    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("motor").setLevel(logging.WARNING)

    return logging.getLogger(__name__)


settings = Settings()
