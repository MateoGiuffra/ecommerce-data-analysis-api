from pandas import DataFrame
from abc import ABC, abstractmethod
from typing import Optional

class MetricsRepository(ABC):
    @abstractmethod
    def get_sheet_name(self) -> str:
        pass
    
    @abstractmethod
    def get_raw_transactions(self) -> DataFrame:
        pass