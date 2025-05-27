from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    geoapify_api_key: str
    openai_api_key: str
    azureai_endpoint: str

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings() -> Settings:
    return Settings()