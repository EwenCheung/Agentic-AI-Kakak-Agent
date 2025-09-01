from functools import lru_cache
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar

import boto3

load_dotenv()

class Settings(BaseSettings):
    AWS_ACCESS_KEY_ID : str | None = None
    AWS_SECRET_ACCESS_KEY : str | None = None
    AWS_REGION : str | None = None

    BEDROCK_MODEL_ID : str | None = None

    @property
    def SESSION(self):
        return boto3.Session(
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
            region_name=self.AWS_REGION,
        )

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra="forbid",
        case_sensitive=True,
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

print("AWS_ACCESS_KEY_ID:", settings.AWS_ACCESS_KEY_ID)
print("AWS_SECRET_ACCESS_KEY:", settings.AWS_SECRET_ACCESS_KEY)
print("AWS_REGION:", settings.AWS_REGION)  
print("BEDROCK_MODEL_ID:", settings.BEDROCK_MODEL_ID)
print("SESSION:", settings.SESSION)