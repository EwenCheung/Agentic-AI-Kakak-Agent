from functools import lru_cache, cached_property
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar

import boto3
import os

load_dotenv()

from sqlalchemy.orm import Session # Added for type hinting
from ..database.models import get_config_db, EnvConfig # Added for database access

class Settings(BaseSettings):
    # AWS
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str | None = None

    # Bedrock
    BEDROCK_MODEL_ID: str | None = None

    # Google Calendar (MCP) integration (re-added for .env fallback)
    GOOGLE_CALENDAR_CREDENTIALS_PATH: str | None = None

    # Raw environment-provided values (DB may override when accessed via getters)
    TELEGRAM_BOT_TOKEN: str | None = None
    TONE_AND_MANNER: str | None = "Friendly and Professional"

    # Embeddings / Vector DB (for knowledge base study)
    EMBED_MODEL_ID: str | None = None
    TOKENIZER_MODEL_ID: str | None = None
    CHROMA_DOC_DB_PATH: str | None = "./src/database/knowledge_base/"
    
    # Mem0 Configuration
    MEM0_LLM_PROVIDER: str | None = "aws_bedrock"
    MEM0_DATA_PATH: str | None = "./src/database/mem0_data"
    MEM0_EMBEDDER_PROVIDER: str | None = "aws_bedrock"
    MEM0_VECTOR_STORE_PROVIDER: str | None = "chroma" 
    
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

    def get_telegram_bot_token(self) -> str | None:
        """Return Telegram bot token, preferring DB over env."""
        try:
            db: Session = next(get_config_db())
            env_config = db.query(EnvConfig).first()
            if env_config and env_config.telegram_bot_token:
                return env_config.telegram_bot_token
        except Exception:
            pass
        return self.TELEGRAM_BOT_TOKEN

    def get_google_client_secret(self) -> str | None:
        """Return Google client secret JSON content.

        Priority/order:
        1. If a value exists in DB, optionally overwrite the file at GOOGLE_CALENDAR_CREDENTIALS_PATH (if set) to keep it in sync, then return DB value.
        2. Else, if a file exists at GOOGLE_CALENDAR_CREDENTIALS_PATH, read and return its content.
        3. Else, return None.
        """
        db_value: str | None = None
        try:
            db: Session = next(get_config_db())
            env_config = db.query(EnvConfig).first()
            if env_config and env_config.client_secret_json:
                db_value = env_config.client_secret_json
        except Exception:
            pass

        # If DB has value, optionally persist/update file
        if db_value:
            path = self.GOOGLE_CALENDAR_CREDENTIALS_PATH
            if path:
                try:
                    # Create parent dirs if needed
                    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
                    # Only write if file missing or content differs
                    needs_write = True
                    if os.path.exists(path):
                        try:
                            with open(path, 'r') as existing:
                                if existing.read() == db_value:
                                    needs_write = False
                        except Exception:
                            pass
                    if needs_write:
                        # Validate JSON before writing
                        import json as _json
                        try:
                            _json.loads(db_value)
                        except Exception:
                            # If invalid JSON, skip writing but still return raw DB value
                            return db_value
                        with open(path, 'w') as f:
                            f.write(db_value)
                except Exception:
                    # Swallow file write errors; still return DB value
                    return db_value
            return db_value

        # Fallback to file
        if self.GOOGLE_CALENDAR_CREDENTIALS_PATH and os.path.exists(self.GOOGLE_CALENDAR_CREDENTIALS_PATH):
            try:
                with open(self.GOOGLE_CALENDAR_CREDENTIALS_PATH, 'r') as f:
                    return f.read()
            except Exception:
                return None
        return None

    def get_tone_and_manner(self) -> str:
        """Return tone & manner from DB or default/env value."""
        try:
            db: Session = next(get_config_db())
            env_config = db.query(EnvConfig).first()
            if env_config and env_config.tone_and_manner:
                return env_config.tone_and_manner
        except Exception:
            pass
        return self.TONE_AND_MANNER or "Friendly and Professional"

    # Convenience alias properties (non-conflicting names)
    @property
    def GOOGLE_CLIENT_SECRET(self) -> str | None:
        return self.get_google_client_secret()
    @property
    def TONE_AND_MANNER_EFFECTIVE(self) -> str:
        return self.get_tone_and_manner()
    
    @property
    def mem0_data_path(self) -> str:
        """Return absolute path for Mem0 data storage"""
        import os
        
        # Convert relative path to absolute
        mem0_path = self.MEM0_DATA_PATH or "./src/database/mem0_data"
        if not os.path.isabs(mem0_path):
            # Get absolute path relative to backend directory
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            mem0_path = os.path.abspath(os.path.join(backend_dir, mem0_path))
        
        # Ensure directory exists
        os.makedirs(mem0_path, exist_ok=True)
        return mem0_path

    def get_mem0_config(self) -> dict:
        """Return complete Mem0 configuration for local/OSS usage"""
        return {
            "llm": {
                "provider": self.MEM0_LLM_PROVIDER or "aws_bedrock",
                "config": {
                    "model": self.BEDROCK_MODEL_ID,
                }
            },
            "embedder": {
                "provider": self.MEM0_EMBEDDER_PROVIDER or "aws_bedrock",
                "config": {
                    "model": self.EMBED_MODEL_ID or "amazon.titan-embed-text-v2:0",
                }
            },
            "vector_store": {
                "provider": self.MEM0_VECTOR_STORE_PROVIDER or "chroma",
                "config": {
                    "collection_name": "mem0",
                    "path": self.mem0_data_path,
                }
            },
            "version": "v1.1"
        }

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

try:
    import logging
    logger = logging.getLogger(__name__)
    logger.info(
        "Config loaded: aws_region=%s bedrock_model=%s",
        settings.AWS_REGION,
        settings.BEDROCK_MODEL_ID,
    )
except Exception:
    pass

