def test_postgres(client):
    response = client.get('/test_postgres')
    assert response.status_code == 200


def test_redis(client):
    response = client.get('/test_redis')
    assert response.status_code == 200
