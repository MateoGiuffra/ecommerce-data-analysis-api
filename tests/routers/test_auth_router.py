from tests.routers.users_constants import *

def test_register_new_user_successfully(client):
    """Integration test: Tests that the /auth/register endpoint registers a new user successfully."""
    response = client.post(
        "/auth/register",  
        json=valid_user
    )
    data = response.json()
 
    assert response.status_code == 201 
    assert data["username"] == name_valid_user
    assert data["is_active"] == True
    assert "id" in data 


def test_register_existing_user_returns_conflict(client):
    """Integration test: Tests that the endpoint returns a 409 Conflict error if trying to register an existing user."""
    client.post(
        "/auth/register", 
        json=valid_user
    )

    response = client.post(
        "/auth/register", 
        json=invalid_user
    )

    assert response.status_code == 409 
    assert response.json()["message"] == "Username already exists"
    

def test_login_without_register_first(client):
    """Tests that logging in without a prior registration returns a 404 Not Found error."""
    response = client.post(
        "/auth/login",
        json=invalid_user
    )
    data = response.json()
    
    assert response.status_code == 404
    assert data["message"] == "User not found"
    
def test_login_with_wrong_password(client):
    """Tests that attempting to log in with an incorrect password returns a 401 Unauthorized error."""
    client.post(
        "/auth/register", 
        json=valid_user
    )

    response = client.post(
        "/auth/login",
        json=invalid_user
    )
    data = response.json()
    
    assert response.status_code == 401
    assert data["message"] == "Invalid password"
    
def test_logout_succesfully(client):
    """Tests that the /auth/logout endpoint works correctly, invalidating the session."""
    response = client.post(
        "/auth/register", 
        json=valid_user
    )
    assert response.status_code == 201
    
    response = client.post(
        "/auth/logout",
        json=valid_user
    )
    
    assert response.status_code == 200
    
    response = client.post(
        "/users"
    )
    
    assert response.status_code == 401
    assert "Unauthorized" in response.json()["message"]
    