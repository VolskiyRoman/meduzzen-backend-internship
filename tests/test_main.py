import requests


def test_status_code_200():
    url = "http://localhost:5000/"
    response = requests.get(url)
    assert response.status_code == 200

