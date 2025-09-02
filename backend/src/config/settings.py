from functools import lru_cache, cached_property
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar

import boto3

load_dotenv()

class Settings(BaseSettings):
    # AWS / Bedrock
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str | None = None
    BEDROCK_MODEL_ID: str | None = None

    # Telegram (optional – used by MCP server). Adding here prevents Pydantic 'extra fields' errors
    TELEGRAM_API_ID: int | None = None
    TELEGRAM_API_HASH: str | None = None
    TELEGRAM_SESSION_NAME: str | None = None
    TELEGRAM_SESSION_STRING: str | None = None

    @cached_property
    def SESSION(self):
        """Lazily create and cache a single boto3 Session instance.

        Using cached_property ensures the session is created only once per
        Settings instance, preventing repeated instantiation that can cause
        credential/provider re-resolution overhead or conflicts in code paths
        expecting a singleton-like session.
        """
        return boto3.Session(
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
            region_name=self.AWS_REGION,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",  # keep strict; we declared all expected vars
        case_sensitive=True,
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

# Avoid printing secrets; provide minimal startup info (can switch to logging if desired)
try:
    import logging
    logger = logging.getLogger(__name__)
    logger.info(
        "Config loaded: aws_region=%s bedrock_model=%s telegram_api_id=%s telegram_session_name=%s",
        settings.AWS_REGION,
        settings.BEDROCK_MODEL_ID,
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_SESSION_NAME,
    )
except Exception:
    pass