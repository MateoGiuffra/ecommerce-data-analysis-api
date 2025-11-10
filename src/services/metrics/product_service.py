from src.services.metrics.metrics_service import MetricsService
from src.services.cache_service import CacheService
from pandas import DataFrame
from pandas.core.resample import DatetimeIndexResampler
from src.repositories.metrics_repository import MetricsRepository
from src.schemas.metrics import *

class ProductService(MetricsService):
    def __init__(self, metrics_repository: MetricsRepository, cache_service: CacheService, cache_df_ttl_seconds: int):
        super().__init__(metrics_repository, cache_service, cache_df_ttl_seconds)
    
    async def get_top_sellers(self, products_metrics_params: ProductMetricsParams): 
        df: DataFrame = await self.get_clean_data_frame()
        top_cellers = (
            df.groupby(self.stock_code)
            .agg(
                total_revenue=(self.total_price, "sum"),
                total_units_sold=(self.quantity, "sum")
            )
            .sort_values(
                by=products_metrics_params.sort_by.value, ascending=products_metrics_params.ascending
            )
            .head(products_metrics_params.limit)
        )
        return [
            Product(product_id=product_id, **row.to_dict())
            for product_id, row in top_cellers.iterrows()
        ]
    
    async def get_specific_product_series(self, product_id: str, serie_type: SerieType):
        df: DataFrame = await self.get_clean_data_frame()
        resampler: DatetimeIndexResampler = df.resample(serie_type.get_resample_kind())
        
        product_serie = resampler.agg(
            revenue=(self.total_price, 'sum'),
            total_units_sold=(self.quantity, 'sum')
        )
        
        return [
            Product(product_id=product_id, **row.to_dict())
            for _, row in product_serie.loc[product_id].items()
        ]
         
    
    