from src.repositories.metrics_repository import MetricsRepository
from pandas import DataFrame
from typing import Optional
import pandas as pd
class MetricsRepositoryLocal(MetricsRepository):
    
    def get_sheet_name(self) -> str:
        return "data"
    
    def get_raw_transactions(self) -> DataFrame:
        return pd.read_csv("data/data.csv", encoding="cp1252")