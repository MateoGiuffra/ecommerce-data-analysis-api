import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.models.user import User
from src.main import app
from src.database.base import Base
from src.database.session import get_db_session as app_get_db_session

SQLALCHEMY_DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool, 
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def client():
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)
    
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[app_get_db_session] = override_get_db

    with TestClient(app) as test_client:
        yield test_client 

    # AFTEREACH
    transaction.rollback() 
    connection.close() 

    app.dependency_overrides.clear()
    

# -------------------------------------------------------------
# 2. FIXTURE DE SERVICIO (USANDO LA SESIÓN DE PRUEBA)
# -------------------------------------------------------------

# Importamos las funciones de inyección necesarias
from src.dependencies.repositories_di import get_user_repository
from src.dependencies.services_di import get_user_service, get_cookie_service 

@pytest.fixture(scope="function")
def user_service_test_instance(_client):
    """
    Fixture that gives a user service instance inyected with the active test session.
    The operations are reversible.
    """
    override_func = app.dependency_overrides.get(app_get_db_session)
    
    if not override_func:
        raise Exception("La dependencia de DB no fue sobrescrita en el fixture 'client'.")
        
    db_generator = override_func()
    db = next(db_generator)

    user_repo = get_user_repository(db=db) 
    cookie_service = get_cookie_service()
    service = get_user_service(
        user_repository=user_repo, 
        cookie_service=cookie_service
    )
    yield service
    
    # AFTEREACH
    try:
        next(db_generator) 
    except StopIteration:
        pass