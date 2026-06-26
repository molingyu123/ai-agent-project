from __future__ import annotations

import logging
from typing import Any

import pandas as pd
from sqlalchemy import inspect, text

from core.database import engine
from core.tools.legacy_adapter import legacy_adapter

logger = logging.getLogger(__name__)


class DataAnalyzerTool:
    """Controlled data access for the analysis agent."""

    def fetch_data(self, data_source: str = "sync_jobs", limit: int = 1000) -> pd.DataFrame:
        if data_source == "legacy":
            result = legacy_adapter.sync_data(system_type="db")
            records = result.get("records", []) if isinstance(result, dict) else []
            return pd.DataFrame(records)

        if data_source == "sync_jobs":
            return self._read_table("sync_jobs", limit=limit)

        if data_source == "documents":
            return self._read_table("documents", limit=limit)

        logger.warning("Unsupported analysis data source: %s", data_source)
        return pd.DataFrame()

    def summarize(self, data: pd.DataFrame | list[dict[str, Any]]) -> str:
        df = pd.DataFrame(data) if isinstance(data, list) else data
        if df.empty:
            return "No data available."

        parts = [f"Rows: {len(df)}, Columns: {len(df.columns)}"]
        numeric_df = df.select_dtypes(include="number")
        if not numeric_df.empty:
            parts.append(numeric_df.describe().to_string())
        else:
            parts.append(df.head(20).to_string(index=False))
        return "\n\n".join(parts)

    def _read_table(self, table_name: str, limit: int = 1000) -> pd.DataFrame:
        inspector = inspect(engine)
        if table_name not in inspector.get_table_names():
            return pd.DataFrame()

        query = text(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT :limit")
        with engine.connect() as conn:
            return pd.read_sql(query, conn, params={"limit": limit})
