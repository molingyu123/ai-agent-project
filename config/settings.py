from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    postgres_url: str
    redis_url: str
    # Add legacy system configs

    class Config:
        env_file = ".env"

settings = Settings()