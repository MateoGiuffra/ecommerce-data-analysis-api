import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from src.main import app
from src.services.user.auth_service import AuthService
from src.services.user.user_service import UserService
from src.dependencies.services_di import get_auth_service, get_user_service
from src.core.config import settings

@pytest.fixture
def user_auth_service_mock():
    mock = MagicMock(spec=AuthService)
    return mock

@pytest.fixture
def user_service_mock():
    mock = MagicMock(spec=UserService)
    return mock

@pytest.fixture
def client(user_auth_service_mock, user_service_mock):
    app.dependency_overrides[get_auth_service] = lambda: user_auth_service_mock
    app.dependency_overrides[get_user_service] = lambda: user_service_mock
    
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def enable_test_mode():
    """Enable TESTING flag for all tests and restore previous value afterwards."""
    previous = getattr(settings, "TESTING", False)
    settings.TESTING = True
    yield
    settings.TESTING = previous