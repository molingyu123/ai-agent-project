import logging
from datetime import timedelta

from celery import Celery

from config.settings import settings
from core.database import init_db
from core.tools.legacy_adapter import legacy_adapter

logger = logging.getLogger(__name__)

app = Celery(
    "ai_agent_tasks",
    broker=settings.redis_url,
    backend=settings.celery_result_backend_url,
)

app.conf.beat_schedule = {
    "sync-legacy-data-every-30-min": {
        "task": "data_pipeline.scheduler.celery_tasks.sync_legacy_data",
        "schedule": timedelta(minutes=30),
        "kwargs": {"system_type": "api"},
    },
    "update-knowledge-base-hourly": {
        "task": "data_pipeline.scheduler.celery_tasks.update_knowledge_base",
        "schedule": timedelta(hours=1),
    },
}
app.conf.timezone = "UTC"


@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def sync_legacy_data(self, system_type: str = "api", **kwargs):
    init_db()
    result = legacy_adapter.sync_data(system_type=system_type, **kwargs)
    logger.info("Legacy sync completed: %s", result)
    return result


@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def update_knowledge_base(self):
    init_db()
    logger.info("Knowledge base update task is ready. Add source-specific indexers here.")
    return {"status": "ready"}


if __name__ == "__main__":
    app.start()
