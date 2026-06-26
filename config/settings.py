from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _load_dotenv(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _env(*names: str, default: str | None = None) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value not in (None, ""):
            return value
    return default


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value in (None, ""):
        return default
    return int(value)


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from .env and environment variables."""

    app_name: str
    environment: str
    log_level: str
    openai_api_key: str | None
    chat_model: str
    embedding_model: str
    postgres_url: str
    redis_url: str
    celery_result_backend_url: str
    vector_store_provider: str
    vector_collection_name: str
    vector_search_k: int
    legacy_db_url: str | None
    legacy_api_base: str | None
    legacy_file_dir: str | None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    _load_dotenv()
    return Settings(
        app_name=_env("APP_NAME", default="AI Agent Project"),
        environment=_env("ENVIRONMENT", default="local"),
        log_level=_env("LOG_LEVEL", default="INFO"),
        openai_api_key=_env("OPENAI_API_KEY"),
        chat_model=_env("CHAT_MODEL", default="gpt-4o-mini"),
        embedding_model=_env("EMBEDDING_MODEL", default="text-embedding-3-small"),
        postgres_url=_env(
            "POSTGRES_URL",
            "DATABASE_URL",
            default="postgresql://user:password@postgres:5432/ai_agent",
        ),
        redis_url=_env("REDIS_URL", default="redis://redis:6379/0"),
        celery_result_backend_url=_env(
            "CELERY_RESULT_BACKEND_URL",
            default="redis://redis:6379/1",
        ),
        vector_store_provider=_env("VECTOR_STORE_PROVIDER", default="pgvector"),
        vector_collection_name=_env("VECTOR_COLLECTION_NAME", default="knowledge_base"),
        vector_search_k=_env_int("VECTOR_SEARCH_K", 6),
        legacy_db_url=_env("LEGACY_DB_URL"),
        legacy_api_base=_env("LEGACY_API_BASE"),
        legacy_file_dir=_env("LEGACY_FILE_DIR"),
    )


settings = get_settings()
