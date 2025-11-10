import pytest
from fastapi import Response, Request
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from src.services.cookie_service import CookieService
from src.database.models.user import User
from src.core.config import settings

@pytest.fixture
def cookie_service():
    """Fixture to get an instance of CookieService."""
    return CookieService()

@pytest.fixture
def sample_user():
    """Fixture to create a sample user."""
    return User(id="a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6", username="testuser", password="testpassword")

def test_create_token(cookie_service: CookieService, sample_user: User):
    """Tests that the JWT token is created correctly."""
    token = cookie_service.create_token(sample_user)
    
    assert isinstance(token, str)
    
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    assert payload["sub"] == sample_user.username
    assert payload["id"] == sample_user.id
    
    # Verifica que la expiración está dentro de un rango razonable
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    expected_exp = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    assert abs((expected_exp - exp_time).total_seconds()) < 5 # Tolerancia de 5 segundos

def test_set_cookie(cookie_service: CookieService, sample_user: User):
    """Tests that the cookie is set correctly in the response."""
    mock_response = MagicMock(spec=Response)
    
    cookie_service.set_cookie(mock_response, sample_user)
    
    mock_response.set_cookie.assert_called_once()
    call_args = mock_response.set_cookie.call_args
    
    assert call_args.kwargs["key"] == "token"
    assert call_args.kwargs["httponly"] is True
    assert call_args.kwargs["samesite"] == "lax"
    assert call_args.kwargs["secure"] == settings.COOKIE_SECURE
    
    # Verifica que el valor de la cookie es un token válido
    token = call_args.kwargs["value"]
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["id"] == sample_user.id

def test_clean_cookies(cookie_service: CookieService):
    """Tests that the cookie is deleted correctly."""
    mock_response = MagicMock(spec=Response)
    
    cookie_service.clean_cookies(mock_response)
    
    mock_response.delete_cookie.assert_called_once_with(key="token", path="/")

def test_get_user_id_from_token_valid(cookie_service: CookieService, sample_user: User):
    """Tests that the user ID is obtained from a valid token in the request."""
    token = cookie_service.create_token(sample_user)
    mock_request = MagicMock(spec=Request)
    mock_request.cookies.get.return_value = token
    
    user_id = cookie_service.get_user_id_from_token(mock_request)
    
    assert user_id == sample_user.id

def test_get_user_id_from_token_invalid(cookie_service: CookieService):
    """Tests that it returns None if the token is invalid."""
    mock_request = MagicMock(spec=Request)
    mock_request.cookies.get.return_value = "invalid.token.string"
    
    user_id = cookie_service.get_user_id_from_token(mock_request)
    
    assert user_id is None

def test_get_user_id_from_token_expired(cookie_service: CookieService, sample_user: User):
    """Tests that it returns None if the token has expired."""
    # Creamos un token que expiró en el pasado
    cookie_service.expiration_time = -1 
    expired_token = cookie_service.create_token(sample_user)
    
    mock_request = MagicMock(spec=Request)
    mock_request.cookies.get.return_value = expired_token
    
    user_id = cookie_service.get_user_id_from_token(mock_request)
    
    assert user_id is None

def test_validate_token_invalid(cookie_service: CookieService):
    """Tests that validate_token raises an exception for an invalid token."""
    previous = getattr(settings, "TESTING", False)
    settings.TESTING = False
    try:
        with pytest.raises(JWTError):
            cookie_service.validate_token("invalid.token")
    finally:
        settings.TESTING = previous

def test_validate_token_none(cookie_service: CookieService):
    """Tests that validate_token raises an exception for a null token."""
    previous = getattr(settings, "TESTING", False)
    settings.TESTING = False
    try:
        with pytest.raises(JWTError):
            cookie_service.validate_token(None)
    finally:
        settings.TESTING = previous