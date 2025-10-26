from gspread import Client
from pandas import DataFrame
from src.repositories.metrics_repository import MetricsRepository

class MetricsRepositoryGspread(MetricsRepository):
    def __init__(self, gspread_client: Client):
        self.client: Client = gspread_client
    
    def get_sheet_name(self) -> str:
        return "data"
        
    def get_raw_transactions(self) -> DataFrame:
            sheet_name: str = self.get_sheet_name()
            sheet_instance = self.client.open(sheet_name).sheet1
            return DataFrame(sheet_instance.get_all_records())
        
            