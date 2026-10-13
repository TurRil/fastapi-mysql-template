from decimal import Decimal

from fastapi.testclient import TestClient
import pytest

from app.api.categorization import Categorization
from app.settings import settings


def test_status_returns_ok(client: TestClient, status_url: str) -> None:
    response = client.get(status_url)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"status": "ok"}


def test_status_is_mounted_under_api(client: TestClient) -> None:
    assert client.get("/status").status_code == 200


def test_status_rejects_post(client: TestClient, status_url: str) -> None:
    response = client.post(status_url)

    assert response.status_code == 405
    assert response.headers["allow"] == "GET"


def test_unknown_api_route_returns_404(client: TestClient) -> None:
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_status_is_documented_in_openapi(client: TestClient, status_url: str) -> None:
    schema = client.get("/openapi.json").json()

    operation = schema["paths"][status_url]["get"]
    assert operation["tags"] == ["api"]
    assert "200" in operation["responses"]


@pytest.fixture
def mock_categorization(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Categorization, "categorize", lambda self, **kwargs: 4)


def test_create_transaction_uses_database_columns(
    client: TestClient, mock_categorization: None
) -> None:
    response = client.post(
        "/transactions",
        json={
            "transaction_id": "TXN00001",
            "amount": -87.18,
            "transaction_date": "2024-05-16T07:22:18.808433",
            "description": "Grocery store",
            "transaction_type": "debit",
            "account_number": "NLINGB1944573686",
        },
    )

    assert response.status_code == 201
    assert response.json()["transaction_id"] == "TXN00001"
    assert response.json()["classification"] == 4
    assert Decimal(response.json()["amount"]) == Decimal("-87.18")


def test_get_transactions_filters_by_classification(
    client: TestClient, mock_categorization: None
) -> None:
    for transaction_id, classification in (("TXN00001", 4), ("TXN00002", 4)):
        response = client.post(
            "/transactions",
            json={
                "transaction_id": transaction_id,
                "amount": 1.20,
                "transaction_date": "2024-05-16T07:22:18",
                "description": "Grocery store",
                "transaction_type": "debit",
                "account_number": "NLINGB1944573686",
            },
        )
        assert response.status_code == 201

    response = client.get("/transactions", params={"classification": 4})

    assert response.status_code == 200
    assert [item["transaction_id"] for item in response.json()] == ["TXN00001", "TXN00002"]


def test_get_transaction_by_id(client: TestClient, mock_categorization: None) -> None:
    client.post(
        "/transactions",
        json={
            "transaction_id": "TXN00001",
            "amount": 1.20,
            "transaction_date": "2024-05-16T07:22:18",
            "description": "Grocery store",
            "transaction_type": "debit",
            "account_number": "NLINGB1944573686",
        },
    )

    response = client.get("/transactions/TXN00001")

    assert response.status_code == 200
    assert response.json()["transaction_id"] == "TXN00001"


def test_get_missing_transaction_returns_404(client: TestClient) -> None:
    response = client.get("/transactions/TXN00000")

    assert response.status_code == 404
