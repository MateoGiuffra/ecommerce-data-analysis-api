from tests.routers.users_constants import *
from src.exceptions.user_exceptions import UserAlreadyExists, UserNotFound, InvalidCredentials
from unittest.mock import ANY
from src.database.models.user import User

def test_register_new_user_successfully(client, user_auth_service_mock):
    """Unit test: Tests that the /auth/register endpoint registers a new user successfully."""
    
    user_auth_service_mock.register.return_value = User(id=1, username=name_valid_user, is_active=True)

    response = client.post("/auth/register", json=valid_user)
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == name_valid_user
    assert data["is_active"] == True
    assert "id" in data
    
    user_auth_service_mock.register.assert_called_once_with(ANY, ANY)


def test_register_existing_user_returns_conflict(client, user_auth_service_mock):
    """Unit test: Tests that the endpoint returns a 409 Conflict error if trying to register an existing user."""
    user_auth_service_mock.register.side_effect = UserAlreadyExists()

    response = client.post("/auth/register", json=valid_user)

    assert response.status_code == 409
    assert response.json()["message"] == "Username already exists"
    user_auth_service_mock.register.assert_called_once_with(ANY, ANY)


def test_login_without_register_first(client, user_auth_service_mock):
    """Unit test: Tests that logging in without a prior registration returns a 404 Not Found error."""
    user_auth_service_mock.login.side_effect = UserNotFound()
    
    response = client.post("/auth/login", json=invalid_user)
    
    assert response.status_code == 404
    assert response.json()["message"] == "User not found"
    user_auth_service_mock.login.assert_called_once_with(ANY, ANY)

    
def test_login_with_wrong_password(client, user_auth_service_mock):
    """Unit test: Tests that attempting to log in with an incorrect password returns a 401 Unauthorized error."""
    user_auth_service_mock.login.side_effect = InvalidCredentials()

    response = client.post("/auth/login", json=invalid_user)
    
    assert response.status_code == 401
    assert response.json()["message"] == "Invalid credentials"
    user_auth_service_mock.login.assert_called_once_with(ANY, ANY)

    
def test_logout_succesfully(client, user_auth_service_mock):
    """Unit test: Tests that the /auth/logout endpoint works correctly, invalidating the session."""
    response = client.post("/auth/logout")
    
    assert response.status_code == 200
    user_auth_service_mock.logout.assert_called_once_with(ANY)