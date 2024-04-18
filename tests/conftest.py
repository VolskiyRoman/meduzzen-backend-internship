from typing import Generator

import pytest
from starlette.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    """creating test client"""
    with TestClient(app) as test_app_client:
        yield test_app_client

