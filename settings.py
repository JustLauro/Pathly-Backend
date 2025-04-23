from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    geoapify_api_key: str
    openai_api_key: str

settings = Settings()
