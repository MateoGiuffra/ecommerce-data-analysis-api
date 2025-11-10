from fastapi import APIRouter, Depends
from src.dependencies.services_di import get_customer_service
from src.services.metrics.customer_service import CustomerService
from typing import List 
from src.schemas.metrics import *


router = APIRouter(prefix="/metrics/customers", tags=["customers"])


@router.get("/rfm", summary="Get RFM Analysis", response_model=List[RFMAnalysis])
async def get_rfm_analysis(customer_service: CustomerService = Depends(get_customer_service)) -> List[RFMAnalysis]:
    rfm_list: List[RFMAnalysis] = await customer_service.get_rfm_analysis()
    return [rfm.model_dump() for rfm in rfm_list]


@router.get("/top-spenders", summary="Get Top Spenders", response_model=List[Spender])
async def get_top_spenders(customer_service: CustomerService = Depends(get_customer_service), top_spenders_params: TopSpendersMetricsParams = Depends(get_top_spenders_params)):
    top_spenders: List[Spender] = await customer_service.get_top_spenders(top_spenders_params)
    return [spender.model_dump() for spender in top_spenders]