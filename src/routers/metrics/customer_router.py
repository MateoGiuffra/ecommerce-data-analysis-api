from fastapi import APIRouter, Depends
from src.dependencies.services_di import get_customer_service
from src.services.metrics.customer_service import CustomerService
from typing import List 
from src.schemas.metrics import *
from src.schemas.pagination import PageParams, get_page_params, PageResponse


router = APIRouter(prefix="/metrics/customers", tags=["customers"])


@router.get("/rfm", summary="Get RFM Analysis", response_model=PageResponse[RFMAnalysis])
async def get_rfm_analysis(customer_service: CustomerService = Depends(get_customer_service), page_params: PageParams = Depends(get_page_params)) -> PageResponse[RFMAnalysis]:
    rfm_page: PageResponse[RFMAnalysis] = await customer_service.get_rfm_analysis_page(page_params)
    rfm_list: List[RFMAnalysis] = rfm_page.results
    rfm_page.results = [rfm.model_dump() for rfm in rfm_list]
    return rfm_page



@router.get("/top-spenders", summary="Get Top Spenders", response_model=List[Spender])
async def get_top_spenders(customer_service: CustomerService = Depends(get_customer_service), top_spenders_params: TopSpendersMetricsParams = Depends(get_top_spenders_params)):
    top_spenders: List[Spender] = await customer_service.get_top_spenders(top_spenders_params)
    return [spender.model_dump() for spender in top_spenders]