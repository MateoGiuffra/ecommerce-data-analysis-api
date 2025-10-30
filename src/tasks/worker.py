import asyncio
import logging
import random
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
    metrics_service: MetricsService = await get_metrics_service_instance()
    await metrics_service.warm_up_dataframe_cache()

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
        raise self.retry(exc=exc)
    finally:
        base_interval = settings.CACHE_DF_TTL_SECONDS // 4

        jitter = base_interval * 0.10 
        random_delay = random.uniform(base_interval - jitter, base_interval + jitter)
        
        logger.info(f"Scheduling next warm_up_dataframe_cache run in {random_delay:.2f} seconds.")
        self.apply_async(countdown=random_delay)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **_kwargs):
    """
    This function is called when the Celery worker starts.
    It triggers the cache warm-up task to run once immediately.
    The task will then reschedule itself in a perpetual loop with jitter.
    """
    logger.info("Triggering initial warm_up_dataframe_cache task on startup.")
    warm_up_dataframe_cache.delay()