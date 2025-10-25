from tests.routers.users_constants import *
import pytest

def test_get_me_succesfully(client):
    """Tests that the /users/me endpoint successfully retrieves the authenticated user's data."""
    response = client.post(
        "/auth/register",  
        json=valid_user
    )
    data = response.json()
 
    assert response.status_code == 201 
    response = client.get(
        "/users/me"
    )
    data = response.json()
    
    assert response.status_code == 200
    assert data["username"] == name_valid_user

def test_get_me_unauthorized(client):
    """Tests that accessing the /users/me endpoint without authentication returns a 401 Unauthorized error."""
    response = client.get(
        "/users/me"
    )
    
    assert response.status_code == 401
    assert "Unauthorized" in response.json()["message"]

# --- Tests for GET /users (paginated results) ---

def test_list_users_unauthorized(client):
    """Tests that listing users without authentication returns a 401 Unauthorized error."""
    response = client.get("/users")
    assert response.status_code == 401
    assert "Unauthorized" in response.json()["message"]

def test_list_users_empty_db(client, user_service_test_instance):
    """Tests that listing users with an empty database returns an empty list."""
    client.post("/auth/register", json=valid_user)
    user_service_test_instance.delete_all()
    
    response = client.get("/users")
    data = response.json()

    assert response.status_code == 200
    assert data["results"] == []
    assert data["total_results"] == 0
    assert data["page"] == 1
    assert data["limit"] == 10

def test_list_users_with_default_pagination(client):
    """Tests the default pagination behavior for the user list endpoint."""
    # Creamos un usuario para poder autenticarnos
    client.post("/auth/register", json=valid_user)

    # Creamos 15 usuarios más para probar la paginación
    for i in range(15):
        client.post("/auth/register", json={"username": f"testuser{i}", "password": "password"})

    # Hay 16 usuarios en total_results
    response = client.get("/users") # page=1, limit=10 por defecto
    data = response.json()

    assert response.status_code == 200
    assert len(data["results"]) == 10
    assert data["total_results"] == 16
    assert data["page"] == 1
    assert data["limit"] == 10

@pytest.mark.parametrize("page, limit", [
    (0, 10),  # page no puede ser 0
    (-1, 10), # page no puede ser negativo
    (1, 0),   # limit no puede ser 0
    (1, -1),  # limit no puede ser negativo
])
def test_list_users_with_invalid_pagination_params(client, page, limit):
    """Tests that invalid pagination parameters return a 422 Unprocessable Entity error."""
    client.post("/auth/register", json=valid_user)
    
    response = client.get(f"/users?page={page}&limit={limit}")
    
    assert response.status_code == 422 # Unprocessable Entity

def test_list_users_requesting_page_out_of_bounds(client):
    """Tests that requesting a page that is out of bounds returns an empty list."""
    client.post("/auth/register", json=valid_user)
    
    response = client.get("/users?page=100") # Solo hay 1 usuario
    data = response.json()

    assert response.status_code == 200
    assert data["results"] == []
    assert data["total_results"] == 1
    assert data["page"] == 100

# --- Tests for GET /users/{id} ---

def test_get_user_by_id_successfully(client):
    """Tests that a user can be successfully retrieved by their ID."""
    reg_response = client.post("/auth/register", json=valid_user)
    user_id = reg_response.json()["id"]

    response = client.get(f"/users/{user_id}")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == user_id
    assert data["username"] == valid_user["username"]

def test_get_user_by_id_not_found(client):
    """Tests that attempting to retrieve a user with a non-existent ID returns a 404 Not Found error."""
    client.post("/auth/register", json=valid_user)
    
    non_existent_id = "12345678-1234-5678-1234-567812345678"
    response = client.get(f"/users/{non_existent_id}")

    assert response.status_code == 404
    assert  response.json()["message"] == f'User with id {non_existent_id} not found'
