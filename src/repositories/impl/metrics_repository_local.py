from src.repositories.metrics_repository import MetricsRepository
from pandas import DataFrame
from typing import Optional
import pandas as pd
class MetricsRepositoryLocal(MetricsRepository):
    
    def get_sheet_name(self) -> str:
        return "data"
    
    def get_raw_transactions(self, n_rows: Optional[int] = None) -> DataFrame:
        return pd.read_csv("data/data.csv", nrows=n_rows, encoding="cp1252")