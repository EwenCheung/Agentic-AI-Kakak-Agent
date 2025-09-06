from functools import lru_cache, cached_property
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar

import boto3

load_dotenv()

class Settings(BaseSettings):
    # AWS
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str | None = None

    # Bedrock
    BEDROCK_MODEL_ID: str | None = None

    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN: str | None = None

    # Google Calendar (MCP) integration
    GOOGLE_CALENDAR_CREDENTIALS_PATH: str | None = None


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
        "Config loaded: aws_region=%s bedrock_model=%s telegram_bot_token_set=%s",
        settings.AWS_REGION,
        settings.BEDROCK_MODEL_ID,
        bool(settings.TELEGRAM_BOT_TOKEN),
    )
except Exception:
    pass

