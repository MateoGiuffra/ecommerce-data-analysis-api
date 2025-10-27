import asyncio
import logging
from celery import Celery
from src.services.metrics_service import MetricsService
from src.core.config import settings
from src.dependencies.tasks import get_metrics_service_instance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

async def _warm_up_cache_async():
    """Helper async function to be called from the sync Celery task."""
    metrics_service = await get_metrics_service_instance()
    await metrics_service.get_clean_data_frame()

@celery_app.task(name="warm_up_dataframe_cache", bind=True, max_retries=3, default_retry_delay=60)
def warm_up_dataframe_cache(self):
    """
    Celery task to pre-calculate and cache the cleaned dataframe.
    This warms up the cache to provide faster responses for the first users.
    """
    try:
        logger.info("Executing task: warm_up_dataframe_cache")
        asyncio.run(_warm_up_cache_async())
        logger.info("Task warm_up_dataframe_cache finished.")
    except Exception as exc:
        logger.error(f"Task warm_up_dataframe_cache failed: {exc}")
        # Retry the task in case of failure
        raise self.retry(exc=exc)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **_kwargs):
    # When the worker starts, trigger the cache warm-up once.
    logger.info("Triggering initial warm_up_dataframe_cache task on startup.")
    warm_up_dataframe_cache.delay()

    # Schedule the task to run periodically.
    logger.info(f"Scheduling warm_up_dataframe_cache to run every {settings.CACHE_DF_TTL_SECONDS} seconds.")
    time_interval = settings.CACHE_DF_TTL_SECONDS - (settings.CACHE_DF_TTL_SECONDS // 2) 
    sender.add_periodic_task(
        time_interval, warm_up_dataframe_cache.s(), name=f'Warm up dataframe cache every {time_interval} seconds'
    )