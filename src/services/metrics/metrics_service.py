from src.repositories.metrics_repository import MetricsRepository
import pandas as pd
import numpy as np
from pandas import DataFrame, Series
from pandas.core.resample import DatetimeIndexResampler
from src.schemas.metrics import KPIsSummary, Serie, SerieType, TopCountryRevenue, TopCountryRevenueParams
from typing import List
from src.exceptions.metrics_exceptions import CountryNotFoundException
from src.exceptions.generic_exceptions import BadRequestException
from src.schemas.pagination import PageParams, PageResponse
from src.services.cache_service import CacheService
from typing import Callable, Awaitable
from src.aspects.caching import Caching
from src.aspects.decorators import excluded_from_cache
import logging

logger = logging.getLogger(__name__)

class MetricsService(metaclass=Caching):
    def __init__(self, metrics_repository: MetricsRepository, cache_service: CacheService, cache_df_ttl_seconds: int):
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
        self.cache_df_ttl_seconds = cache_df_ttl_seconds
        
        
    def _clean_and_convert_to_numeric(self, series: pd.Series) -> Series:
        """
        Cleans a pandas Series by removing commas and stripping whitespace,
        then converts it to a numeric type. Non-convertible values become 0.
        """
        cleaned = series.astype(str).str.replace(",", "").str.strip()

        numeric = pd.to_numeric(cleaned, errors="coerce")

        numeric = numeric.replace([pd.NA, pd.NaT], np.nan)
        try:
            mask_finite = np.isfinite(numeric.values)
            numeric.loc[~mask_finite] = np.nan
        except Exception:
            numeric = numeric.replace([np.inf, -np.inf, float('inf'), -float('inf')], np.nan)

        numeric = numeric.fillna(0.0)
        return numeric.astype(float)
    
    @excluded_from_cache
    def _process_dataframe(self, df: DataFrame) -> DataFrame:
        """Processes the raw dataframe by cleaning, transforming, and adding columns."""
        if df.empty:
            return df
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        self._validate_columns(df)

        df[self.quantity] = self._clean_and_convert_to_numeric(df[self.quantity])
        df[self.unit_price] = self._clean_and_convert_to_numeric(df[self.unit_price])

        # Parse dates safely; coerce invalid parse to NaT and drop those rows
        df[self.invoice_date] = pd.to_datetime(df[self.invoice_date], errors="coerce")
        if df[self.invoice_date].isna().any():
            logger.warning(f"Found {df[self.invoice_date].isna().sum()} rows with invalid {self.invoice_date}; dropping them")
            df = df[df[self.invoice_date].notna()].copy()

        df[self.total_price] = df[self.quantity] * df[self.unit_price]
        df[self.customer_id] = df[self.customer_id].astype(str).str.strip()
        df[self.stock_code] = df[self.stock_code].astype(str).str.strip()
        df[self.invoice_no] = df[self.invoice_no].astype(str).str.strip()

        try:
            df = df.set_index(self.invoice_date, drop=False)
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
        except Exception as e:
            logger.exception(f"Failed to set index on dataframe using {self.invoice_date}: {e}")

        return df

    @excluded_from_cache
    async def warm_up_dataframe_cache(self) -> None:
        raw_df: DataFrame = self.metrics_repository.get_raw_transactions()
        df = self._process_dataframe(raw_df)
        await self.cache_service.set_dataframe(self.df_cache_key, df, self.cache_df_ttl_seconds)

    def _get_clean_data_frame(self) -> Callable[[], Awaitable[DataFrame]]:
        """
        Returns a memoized, decorated, and cached version of the data fetching logic.
        The decorated function is created only once per service instance.
        """
        @self.cache_service.cache_dataframe(key=self.df_cache_key, ttl_seconds=self.cache_df_ttl_seconds)
        async def _fetch_and_clean_dataframe() -> DataFrame:
            """This function contains the actual data processing logic."""
            raw_df: DataFrame = self.metrics_repository.get_raw_transactions()
            return self._process_dataframe(raw_df)
        
        return _fetch_and_clean_dataframe
    
    @excluded_from_cache
    async def get_clean_data_frame(self) -> DataFrame:
        return await self._get_clean_data_frame()()

    @excluded_from_cache
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
        df: DataFrame = await self.get_clean_data_frame()
        
        return KPIsSummary(
            total_revenue=float(df[self.total_price].sum()),
            total_products_sold=int(df[self.quantity].sum()),
            average_total_products_sold=float(df[self.quantity].mean())
        )
        
        
    async def get_series(self, serie_type: SerieType) -> List[Serie]:
        df: DataFrame = await self.get_clean_data_frame()
        
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
        df: DataFrame = await self.get_clean_data_frame()

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

        df: DataFrame = await self.get_clean_data_frame()
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
        df: DataFrame = await self.get_clean_data_frame()
        total_results = len(df)
        total_pages = (total_results + page_params.limit - 1) // page_params.limit if total_results > 0 else 0
        
        return PageResponse(
            results=df.iloc[page_params.offset:page_params.offset + page_params.limit].to_dict(orient="records"),
            page=page_params.page,
            limit=page_params.limit,
            total_pages=total_pages,
            total_results=total_results
        )