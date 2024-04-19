from fastapi.testclient import TestClient


def test_create_user(test_client: TestClient):
    """ Testing creating user """
    response = test_client.post("/users", json={
        "username": "some_username",
        "email": "somemail@gmail.com",
        "password": "<PASSWORD>",
        "is_admin": False
    })
    assert response.status_code == 200


def test_get_all_users(test_client: TestClient):
    """ Testing getting all users """
    response = test_client.get("/users")
    assert response.status_code == 200
