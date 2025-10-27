from src.repositories.metrics_repository import MetricsRepository
import pandas as pd
from pandas import DataFrame, Series
from pandas.core.resample import DatetimeIndexResampler
from src.schemas.metrics import KPIsSummary, Serie, SerieType, TopCountryRevenue, TopCountryRevenueParams
from typing import List
from src.exceptions.metrics_exceptions import CountryNotFoundException
from src.exceptions.generic_exceptions import BadRequestException
from src.schemas.pagination import PageParams, PageResponse
from src.services.cache_service import CacheService
from typing import Callable, Awaitable, Optional
from src.aspects.caching import Caching
from src.aspects.decorators import excluded_from_cache

class MetricsService(metaclass=Caching):
    def __init__(self, metrics_repository: MetricsRepository, cache_service: CacheService, cache_ttl_seconds: int):
        self.metrics_repository: MetricsRepository = metrics_repository
        self.invoice_no: str = "invoiceno"
        self.stock_code: str = "stockcode"
        self.description: str = "description"
        self.quantity: str = "quantity"
        self.invoice_date: str = "invoicedate"
        self.unit_price: str = "unitprice"
        self.customer_id: str = "customerid"
        self.country: str = "country"
        self.total_price: str = "total_price"
        
        self.cache_service = cache_service
        self.df_cache_key = "metrics:clean_dataframe"
        self.cache_ttl = cache_ttl_seconds
        
    def _clean_and_convert_to_numeric(self, series: pd.Series) -> Series:
        """
        Cleans a pandas Series by removing commas and stripping whitespace,
        then converts it to a numeric type. Non-convertible values become 0.
        """
        series = pd.to_numeric(
            series.astype(str).str.replace(",", "").str.strip(),
            errors="coerce"
        ).fillna(0)
        return series.astype(float)


    
    @excluded_from_cache
    def _get_clean_data_frame(self) -> Callable[[], Awaitable[DataFrame]]:
        """
        Returns a memoized, decorated, and cached version of the data fetching logic.
        The decorated function is created only once per service instance.
        """
        @self.cache_service.cache_dataframe(key=self.df_cache_key, ttl_seconds=self.cache_ttl)
        async def _fetch_and_clean_dataframe() -> DataFrame:
            """This function contains the actual data processing logic."""
            df: DataFrame = self.metrics_repository.get_raw_transactions()
            if df.empty:
                return df
            
            df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
            self._validate_columns(df)
            df[self.quantity] = self._clean_and_convert_to_numeric(df[self.quantity])
            df[self.unit_price] = self._clean_and_convert_to_numeric(df[self.unit_price])
            df[self.invoice_date] = pd.to_datetime(df[self.invoice_date])
            df[self.total_price] = df[self.quantity] * df[self.unit_price]
            df = df.set_index(self.invoice_date)
            return df
        
        return _fetch_and_clean_dataframe

    def _validate_columns(self, df: DataFrame):
        required_columns = [
            self.invoice_no,
            self.stock_code,
            self.description,
            self.quantity,
            self.invoice_date,
            self.unit_price,
            self.customer_id,
            self.country
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise KeyError(f"Missing required columns: {', '.join(missing_columns)}")
        

    async def get_kpi_summary(self) -> KPIsSummary:
        df: DataFrame = await self._get_clean_data_frame()()
        
        return KPIsSummary(
            total_revenue=float(df[self.total_price].sum()),
            total_products_sold=int(df[self.quantity].sum()),
            average_total_products_sold=float(df[self.quantity].mean())
        )
        
        
    async def get_series(self, serie_type: SerieType) -> List[Serie]:
        df: DataFrame = await self._get_clean_data_frame()()
        
        resampler: DatetimeIndexResampler = df.resample(serie_type.get_resample_kind())

        summary = resampler.agg(
            revenue=(self.total_price, 'sum'),
            products_sold=(self.quantity, 'sum')
        )
        
        summary['growth_rate'] = (
            summary['revenue']
            .pct_change()
            .replace([pd.NA, float('inf'), -float('inf')], 0)
            .fillna(0) * 100
        )
      
        return [
            Serie(period=index.strftime('%Y-%m-%d'),**row.to_dict())
            for index, row in summary.iterrows()
        ]
    
    
    async def get_top_countries(self, countries_params: TopCountryRevenueParams) -> List[TopCountryRevenue]:
        df: DataFrame = await self._get_clean_data_frame()()

        top_countries_df = (
            df.groupby(self.country)
            .agg(revenue=(self.total_price, "sum"), products_sold=(self.quantity, "sum"))
            .sort_values(
                by=countries_params.sort_value.value, ascending=countries_params.ascending
            )
            .head(countries_params.limit)
        )
            
        return [
            TopCountryRevenue(country=country, **row.to_dict())
            for country, row in top_countries_df.iterrows()
        ]
    
    async def get_top_country_by_name(self, country_name: str) -> TopCountryRevenue | None:
        if country_name is None or country_name.strip() == "":
            raise BadRequestException("Country name is required")

        df: DataFrame = await self._get_clean_data_frame()()
        condition = df[self.country] == country_name
        top_country_df = (
            df[condition]
            .groupby(self.country)
            .agg(revenue=(self.total_price, "sum"), products_sold=(self.quantity, "sum"))
            .sort_values(by="revenue", ascending=False)
            .head(1)
        )
        if top_country_df.empty:
            raise CountryNotFoundException(country_name)
        
        return TopCountryRevenue(country=country_name, **top_country_df.iloc[0].to_dict())

        
    async def get_page(self, page_params: PageParams) -> PageResponse:
        df: DataFrame = await self._get_clean_data_frame()()
        total_results = len(df)
        total_pages = (total_results + page_params.limit - 1) // page_params.limit if total_results > 0 else 0
        
        return PageResponse(
            results=df.iloc[page_params.offset:page_params.offset + page_params.limit].to_dict(orient="records"),
            page=page_params.page,
            limit=page_params.limit,
            total_pages=total_pages,
            total_results=total_results
        )