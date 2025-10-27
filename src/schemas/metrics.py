from pydantic import BaseModel, Field
from enum import Enum
from fastapi import Query
# ----------------------------------------------------------------------
# Base Models
# ----------------------------------------------------------------------
class MetricBaseModel(BaseModel):
    currency: str = Field("USD", description="Currency used in the calculations.")

# ----------------------------------------------------------------------
# Schemas for KPI Summary Endpoint
# ----------------------------------------------------------------------
class KPIsSummary(MetricBaseModel):
    total_revenue: float = Field(..., description="Total revenue generated.")
    total_products_sold: int = Field(..., description="Total number of products sold.")
    average_total_products_sold: float = Field(..., description="Average number of products sold.")

# ----------------------------------------------------------------------
# Schemas and Dependencies for Time Series Endpoint
# ----------------------------------------------------------------------
class Serie(MetricBaseModel):
    period: str = Field(..., description="Period of the data in YYYY-MM-DD (year-month-day)")
    revenue: float = Field(..., description="Revenue generated in the period.")
    products_sold: int = Field(..., description="Number of products sold in the period.")
    growth_rate: float = Field(..., description="Growth rate of the revenue compared to the previous period.")

class SerieType(str, Enum):
    MONTH = "month"
    WEEK = "week"
    YEAR = "year"
    DAY = "day"
    
    def get_resample_kind(self) -> str:
        match self.value:
            case "month":
                return "ME"
            case "week":
                return "W"
            case "year":
                return "Y"
            case "day":
                return "D"

def get_series_params(serie_type: SerieType = Query(SerieType.MONTH, description="Type of the series")) -> SerieType:
    return serie_type

# ----------------------------------------------------------------------
# Schemas and Dependencies for Top Countries Endpoint
# ----------------------------------------------------------------------
class TopCountryRevenue(MetricBaseModel):
    country: str = Field(..., description="Country name.")
    revenue: float = Field(..., description="Revenue generated in the country.")
    products_sold: int = Field(..., description="Number of products sold in the country.")

class SortValue(str, Enum):
    REVENUE = "revenue"
    PRODUCTS_SOLD = "products_sold"
    
class TopCountryRevenueParams(BaseModel):
    limit: int = Field(10, description="Number of countries to return.")
    ascending: bool = Field(False, description="Sort in ascending order.")
    sort_value: SortValue = Field(SortValue.REVENUE, description="Field to sort by.")
    
def get_top_countries_params(limit: int = Query(10, description="Number of countries to return."), 
                             ascending: bool = Query(False, description="Sort in ascending order by sort value."), 
                             sort_value: SortValue = Query(SortValue.REVENUE, description="Field to sort by.")
                             )-> TopCountryRevenueParams:
    return TopCountryRevenueParams(
        limit=limit,
        ascending=ascending,
        sort_value=sort_value
    )
