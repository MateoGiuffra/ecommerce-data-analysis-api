from fastapi import APIRouter, Depends
from src.dependencies.services_di import get_metrics_service, get_cache_service
from src.services.metrics.metrics_service import MetricsService

router = APIRouter(prefix="/admin", tags=["admin"])

@router.delete("/cache", status_code=200)
async def clear_cache(cache_service = Depends(get_cache_service)):
    await cache_service.delete_cache()
    return {"message": "Cache cleared successfully"}
    
@router.post("/tasks/warm-up-cache")
async def clear_cache(metrics_service: MetricsService = Depends(get_metrics_service)):
    await metrics_service.warm_up_dataframe_cache()
    return {"message": "Cache warmed up successfully"}