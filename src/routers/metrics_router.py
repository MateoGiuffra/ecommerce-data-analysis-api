from src.routers import *
from src.dependencies.services_di import get_metrics_service
from src.services.metrics_service import MetricsService
from fastapi import APIRouter
from src.schemas.pagination import PageParams, get_page_params, PageResponse
from src.schemas.metrics import KPIsSummary, Serie, TopCountryRevenue
from typing import List
from src.schemas.metrics import *


router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.get("/kpi_summary")
def get_kpi_summary(metrics_service : MetricsService = Depends(get_metrics_service)) -> KPIsSummary:
    kpi_summary: KPIsSummary =  metrics_service.get_kpi_summary()
    return kpi_summary.model_dump()

@router.get("/series")
def get_series(metrics_service : MetricsService = Depends(get_metrics_service), serie_type: SerieType = Depends(get_series_params)) -> List[Serie]:
    series: List[Serie] = metrics_service.get_series(serie_type)
    return [serie.model_dump() for serie in series]

@router.get("/top_countries")
def get_top_countries(metrics_service: MetricsService = Depends(get_metrics_service), 
                      countries_params: TopCountryRevenueParams = Depends(get_top_countries_params)) -> List[TopCountryRevenue]:
    top_countries: List[TopCountryRevenue] = metrics_service.get_top_countries(countries_params)
    return [top_country.model_dump() for top_country in top_countries]

@router.get("/top_countries/{country_name}") 
def get_top_country_by_name(country_name: str, metrics_service: MetricsService = Depends(get_metrics_service)) -> TopCountryRevenue:
    top_country: TopCountryRevenue = metrics_service.get_top_country_by_name(country_name)
    return top_country.model_dump()

@router.get("/page")
def get_page(metrics_service: MetricsService = Depends(get_metrics_service), page_params: PageParams = Depends(get_page_params)) -> PageResponse:
    page: PageResponse = metrics_service.get_page(page_params)
    return page.model_dump()

