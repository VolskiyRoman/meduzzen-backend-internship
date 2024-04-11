def test_status_code_200(client):
    response = client.get("/")
    assert response.status_code == 200


