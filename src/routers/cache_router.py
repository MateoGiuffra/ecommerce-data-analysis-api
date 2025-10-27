from fastapi import APIRouter,Depends
from src.dependencies.services_di import get_cache_service

router = APIRouter(prefix="/cache", tags=["cache"])
@router.delete("", status_code=200)
async def clear_cache(cache_service = Depends(get_cache_service)):
    await cache_service.delete_cache()
    return {"message": "Cache cleared successfully"}