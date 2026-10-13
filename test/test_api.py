from fastapi.testclient import TestClient

from app.settings import settings


def test_status_returns_ok(client: TestClient, status_url: str) -> None:
    response = client.get(status_url)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"status": "ok"}


def test_status_is_mounted_under_api_prefix(client: TestClient) -> None:
    assert client.get("/status").status_code == 404


def test_status_rejects_post(client: TestClient, status_url: str) -> None:
    response = client.post(status_url)

    assert response.status_code == 405
    assert response.headers["allow"] == "GET"


def test_unknown_api_route_returns_404(client: TestClient) -> None:
    response = client.get(f"{settings.api_prefix}/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_status_is_documented_in_openapi(client: TestClient, status_url: str) -> None:
    schema = client.get("/openapi.json").json()

    operation = schema["paths"][status_url]["get"]
    assert operation["tags"] == ["api"]
    assert "200" in operation["responses"]
