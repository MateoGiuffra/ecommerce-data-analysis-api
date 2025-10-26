from gspread import Client
from pandas import DataFrame
from typing import List, Dict, Union, Optional
from src.repositories.metrics_repository import MetricsRepository

class MetricsRepositoryGspread(MetricsRepository):
    def __init__(self, gspread_client: Client):
        self.client: Client = gspread_client
    
    def get_sheet_name(self) -> str:
        return "data"
        
    def get_raw_transactions(self, n_rows: Optional[int] = None) -> DataFrame:
            sheet_name: str = self.get_sheet_name()
            sheet_instance = self.client.open(sheet_name).sheet1

            if n_rows is None:
                records: List[Dict[str, Union[int, float, str]]] = sheet_instance.get_all_records()
                return DataFrame(records)

            rows = sheet_instance.get_all_values()
            if not rows:
                return DataFrame()

            header = [str(c).strip().replace('"', '').replace("'", "") for c in rows[0]]
            data_rows = rows[1:1 + n_rows] 

            df = DataFrame(data_rows, columns=header)
            df.columns = df.columns.astype(str).str.strip()
            return df