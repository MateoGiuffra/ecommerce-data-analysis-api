from src.repositories.metrics_repository import MetricsRepository
import pandas as pd
from pandas import DataFrame, Series
from pandas.core.resample import DatetimeIndexResampler
from src.schemas.metrics import KPIsSummary, Serie, SerieType, TopCountryRevenue, TopCountryRevenueParams
from typing import List


class MetricsService:
    def __init__(self, metrics_repository: MetricsRepository):
        self.metrics_repository: MetricsRepository = metrics_repository
        self.invoice_no: str = "invoiceno"
        self.stock_code: str = "stockcode"
        self.description: str = "description"
        self.quantity: str = "quantity"
        self.invoice_date: str = "invoicedate"
        self.unit_price: str = "unitprice"
        self.customer_id: str = "customerid"
        self.country: str = "country"

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
    
    def _get_clean_data_frame(self) -> DataFrame:
        df: DataFrame = self.metrics_repository.get_raw_transactions()
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        self._validate_columns(df)

        df[self.quantity] = self._clean_and_convert_to_numeric(df[self.quantity])
        df[self.unit_price] = self._clean_and_convert_to_numeric(df[self.unit_price])
        df[self.invoice_date] = pd.to_datetime(df[self.invoice_date])

        df['total_price'] = df[self.quantity] * df[self.unit_price]

        df = df.set_index(self.invoice_date)
        return df
    
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
        

    def get_kpi_summary(self) -> KPIsSummary:
        df: DataFrame = self._get_clean_data_frame()
        
        return KPIsSummary(
            total_revenue=float(df['total_price'].sum()),
            total_products_sold=int(df[self.quantity].sum()),
            average_total_products_sold=float(df[self.quantity].mean())
        )
        
        
    def get_series(self, serie_type: SerieType) -> List[Serie]:
        df: DataFrame = self._get_clean_data_frame()
        
        resampler: DatetimeIndexResampler = df.resample(serie_type.get_resample_kind())

        summary = resampler.agg(
            revenue=('total_price', 'sum'),
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
    
    
    def get_top_countries(self, countries_params: TopCountryRevenueParams) -> List[TopCountryRevenue]:
        df: DataFrame = self._get_clean_data_frame()

        top_countries_df = (
            df.groupby(self.country)
            .agg(revenue=("total_price", "sum"), products_sold=(self.quantity, "sum"))
            .sort_values(
                by=countries_params.sort_value.value, ascending=countries_params.ascending
            )
            .head(countries_params.limit)
        )
            
        return [
            TopCountryRevenue(country=country, **row.to_dict())
            for country, row in top_countries_df.iterrows()
        ]

    