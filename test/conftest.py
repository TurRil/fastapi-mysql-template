from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.settings import settings
from main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def status_url() -> str:
    return f"{settings.api_prefix}/status"
