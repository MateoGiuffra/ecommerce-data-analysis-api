# ----------------------------------------------------------------------
# UserRepository
# ----------------------------------------------------------------------

from src.database.session import get_db_session
from src.repositories.impl.user_repository_sql_alchemy import *
from sqlalchemy.orm import Session
from fastapi import Depends

def get_user_repository(db: Session = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db=db)

# ----------------------------------------------------------------------
# MetricsRepository
# ----------------------------------------------------------------------

from gspread import Client
from src.dependencies.gspread_client import get_gspread_client
from src.repositories.impl.metrics_repository_gspread import MetricsRepositoryGspread
from src.repositories.metrics_repository import MetricsRepository
from src.repositories.impl.metrics_repository_local import MetricsRepositoryLocal

def get_metrics_repository(_gspread_client: Client = Depends(get_gspread_client)) -> MetricsRepository:
    # return MetricsRepositoryLocal()
    return MetricsRepositoryGspread(_gspread_client)