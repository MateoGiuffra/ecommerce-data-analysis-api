from src.database.session import get_db_session
from src.repositories.impl.user_repository_sql_alchemy import *
from sqlalchemy.orm import Session
from fastapi import Depends

def get_user_repository(db: Session = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db=db)
