from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from src.core.config import settings


engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()
