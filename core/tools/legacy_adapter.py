"""
Legacy System Adapter - Supports integration with old business systems.
Supports REST, Database, File-based legacy systems.
"""

import requests
import pandas as pd
from sqlalchemy import create_engine
from typing import Dict, Any, List
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class LegacyAdapter:
    def __init__(self):
        self.config = {}  # Load from config/legacy_connectors.yaml in production
    
    def fetch_from_api(self, endpoint: str, params: Dict = None) -> Dict:
        """Fetch data from legacy REST API"""
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Legacy API fetch failed: {e}")
            return {"error": str(e)}
    
    def fetch_from_db(self, query: str, db_url: str = None) -> pd.DataFrame:
        """Fetch data from legacy database"""
        try:
            engine = create_engine(db_url or settings.postgres_url)
            df = pd.read_sql(query, engine)
            return df
        except Exception as e:
            logger.error(f"Legacy DB fetch failed: {e}")
            return pd.DataFrame()
    
    def sync_data(self, system_type: str = "api") -> bool:
        """Sync data to vector store / main DB"""
        logger.info(f"Syncing from legacy {system_type}")
        # TODO: Implement ETL to knowledge_base and analysis
        return True

# Tool for LangGraph
legacy_adapter = LegacyAdapter()