from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    postgres_url: str
    redis_url: str = "redis://redis:6379/0"
    # Legacy system configs (loaded from YAML in prod)
    legacy_db_url: str | None = None
    legacy_api_base: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
