from tests.routers.users_constants import *
import pytest
from src.exceptions.user_exceptions import UserNotFound
from src.schemas.pagination import PageResponse
from src.database.models.user import User
from unittest.mock import ANY

@pytest.fixture(autouse=True)
def authorize_request(client):
    client.cookies.update({"session": "some-session-token"})

def test_get_me_succesfully(client, user_service_mock):
    """Unit test: Tests that the /users/me endpoint successfully retrieves the authenticated user's data."""
    user_service_mock.get_current_user.return_value = User(id=1, username=name_valid_user)
    
    response = client.get("/users/me")
    data = response.json()
    
    assert response.status_code == 200
    assert data["username"] == name_valid_user
    user_service_mock.get_current_user.assert_called_once_with(ANY)


def test_list_users_empty_db(client, user_service_mock):
    """Unit test: Tests that listing users with an empty database returns an empty list."""
    user_service_mock.list_users.return_value = PageResponse(results=[], total_results=0, page=1, limit=10, total_pages=0)
    
    response = client.get("/users")
    data = response.json()

    assert response.status_code == 200
    assert data["results"] == []
    assert data["total_results"] == 0
    assert data["page"] == 1
    assert data["limit"] == 10
    user_service_mock.list_users.assert_called_once_with(ANY)


def test_list_users_with_default_pagination(client, user_service_mock):
    """Unit test: Tests the default pagination behavior for the user list endpoint."""
    users = [User(id=i, username=f"testuser{i}") for i in range(10)]
    user_service_mock.list_users.return_value = PageResponse(results=users, total_results=16, page=1, limit=10, total_pages=2)

    response = client.get("/users")
    data = response.json()

    assert response.status_code == 200
    assert len(data["results"]) == 10
    assert data["total_results"] == 16
    assert data["page"] == 1
    assert data["limit"] == 10
    user_service_mock.list_users.assert_called_once_with(ANY)


@pytest.mark.parametrize("page, limit", [
    (0, 10),
    (-1, 10),
    (1, 0),
    (1, -1),
])
def test_list_users_with_invalid_pagination_params(client, page, limit):
    """Tests that invalid pagination parameters return a 422 Unprocessable Entity error."""
    response = client.get(f"/users?page={page}&limit={limit}")
    assert response.status_code == 422


def test_list_users_requesting_page_out_of_bounds(client, user_service_mock):
    """Unit test: Tests that requesting a page that is out of bounds returns an empty list."""
    user_service_mock.list_users.return_value = PageResponse(results=[], total_results=1, page=100, limit=10, total_pages=1)
    
    response = client.get("/users?page=100")
    data = response.json()

    assert response.status_code == 200
    assert data["results"] == []
    assert data["total_results"] == 1
    assert data["page"] == 100
    user_service_mock.list_users.assert_called_once_with(ANY)


def test_get_user_by_id_successfully(client, user_service_mock):
    """Unit test: Tests that a user can be successfully retrieved by their ID."""
    user_id = "some-uuid"
    user_service_mock.get_user_by_id.return_value = User(id=user_id, username=valid_user["username"])

    response = client.get(f"/users/{user_id}")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == user_id
    assert data["username"] == valid_user["username"]
    user_service_mock.get_user_by_id.assert_called_once_with(user_id)


def test_get_user_by_id_not_found(client, user_service_mock):
    """Unit test: Tests that attempting to retrieve a user with a non-existent ID returns a 404 Not Found error."""
    non_existent_id = "12345678-1234-5678-1234-567812345678"
    user_service_mock.get_user_by_id.side_effect = UserNotFound(detail=f"User with id {non_existent_id} not found")
    
    response = client.get(f"/users/{non_existent_id}")

    assert response.status_code == 404
    assert response.json()["message"] == f"User with id {non_existent_id} not found"
    user_service_mock.get_user_by_id.assert_called_once_with(non_existent_id)
