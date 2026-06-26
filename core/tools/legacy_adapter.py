from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from sqlalchemy import create_engine, text

from config.settings import settings
from core.database import SyncJob, session_scope
from knowledge_base.indexer import KnowledgeIndexer

logger = logging.getLogger(__name__)


class LegacyAdapter:
    """Adapter layer for REST, database, and file-based legacy systems."""

    def __init__(self):
        self.indexer = KnowledgeIndexer()

    def fetch_from_api(self, endpoint: str | None = None, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if endpoint is None:
            if not settings.legacy_api_base:
                return {"records": [], "error": "LEGACY_API_BASE is not configured."}
            endpoint = settings.legacy_api_base

        response = requests.get(endpoint, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return {"records": data}
        if isinstance(data, dict) and "records" in data:
            return data
        return {"records": [data]}

    def fetch_from_db(
        self,
        query: str = "SELECT 1 AS health_check",
        db_url: str | None = None,
    ) -> pd.DataFrame:
        engine = create_engine(db_url or settings.legacy_db_url or settings.postgres_url, pool_pre_ping=True)
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn)

    def fetch_from_files(self, directory: str | None = None) -> list[dict[str, Any]]:
        root = Path(directory or settings.legacy_file_dir or "data")
        if not root.exists():
            return []

        records: list[dict[str, Any]] = []
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".txt", ".md", ".csv", ".json"}:
                continue
            try:
                records.append(
                    {
                        "path": str(path),
                        "name": path.name,
                        "content": path.read_text(encoding="utf-8"),
                    }
                )
            except UnicodeDecodeError:
                logger.warning("Skipping non-UTF-8 legacy file: %s", path)
        return records

    def sync_data(self, system_type: str = "api", **kwargs) -> dict[str, Any]:
        """Sync legacy data into metadata tables and the knowledge base."""

        source = f"legacy:{system_type}"
        job_id: int | None = None
        records_read = 0
        records_written = 0

        with session_scope() as session:
            job = SyncJob(source=source, status="running", metadata_json=kwargs)
            session.add(job)
            session.flush()
            job_id = job.id

        try:
            records = self._fetch_records(system_type, **kwargs)
            records_read = len(records)
            warning = None
            if records:
                if settings.openai_api_key:
                    index_result = self.indexer.index_records(records, source=source)
                    records_written = index_result.get("indexed", 0)
                else:
                    warning = "OPENAI_API_KEY is not configured; skipped vector indexing."

            with session_scope() as session:
                job = session.get(SyncJob, job_id)
                job.status = "success"
                job.finished_at = datetime.utcnow()
                job.records_read = records_read
                job.records_written = records_written

            return {
                "job_id": job_id,
                "status": "success",
                "records_read": records_read,
                "records_written": records_written,
                "records": records[:20],
                "warning": warning,
            }
        except Exception as exc:
            logger.exception("Legacy sync failed")
            with session_scope() as session:
                job = session.get(SyncJob, job_id)
                job.status = "failed"
                job.finished_at = datetime.utcnow()
                job.records_read = records_read
                job.records_written = records_written
                job.error_message = str(exc)
            return {
                "job_id": job_id,
                "status": "failed",
                "records_read": records_read,
                "records_written": records_written,
                "error": str(exc),
            }

    def _fetch_records(self, system_type: str, **kwargs) -> list[dict[str, Any]]:
        if system_type == "api":
            result = self.fetch_from_api(kwargs.get("endpoint"), kwargs.get("params"))
            return result.get("records", [])

        if system_type == "db":
            df = self.fetch_from_db(kwargs.get("query", "SELECT 1 AS health_check"), kwargs.get("db_url"))
            return df.to_dict(orient="records")

        if system_type == "file":
            return self.fetch_from_files(kwargs.get("directory"))

        raise ValueError(f"Unsupported legacy system type: {system_type}")


legacy_adapter = LegacyAdapter()
