"""
Celery tasks for scheduled data listening and syncing.
"""

from celery import Celery
from datetime import timedelta
from core.tools.legacy_adapter import legacy_adapter
import logging

logger = logging.getLogger(__name__)

app = Celery('ai_agent_tasks',
             broker='redis://redis:6379/0',
             backend='redis://redis:6379/1')

app.conf.beat_schedule = {
    'sync-legacy-data-every-30-min': {
        'task': 'data_pipeline.scheduler.celery_tasks.sync_legacy_data',
        'schedule': timedelta(minutes=30),
    },
    'update-knowledge-base-hourly': {
        'task': 'data_pipeline.scheduler.celery_tasks.update_knowledge_base',
        'schedule': timedelta(hours=1),
    },
}

@app.task
def sync_legacy_data():
    """Periodic sync from legacy systems"""
    try:
        success = legacy_adapter.sync_data()
        logger.info(f"Legacy sync completed: {success}")
        return success
    except Exception as e:
        logger.error(f"Sync task failed: {e}")
        return False

@app.task
def update_knowledge_base():
    """Update RAG knowledge base"""
    logger.info("Updating knowledge base...")
    # TODO: Call indexer
    return True

if __name__ == '__main__':
    app.start()