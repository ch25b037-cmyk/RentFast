from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from tests.test_loans import setup_loan


def login(email_prefix: str) -> tuple[TestClient, str]:
    email = f"{email_prefix}+{uuid4().hex[:8]}@example.edu"
    client = TestClient(app)
    client.post("/api/v1/auth/otp/request", json={"email": email})
    response = client.post("/api/v1/auth/otp/verify", json={"email": email, "code": app.state.last_otp})
    return client, response.json()["access_token"]


def test_security_headers_and_cors_are_present() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"

    preflight = client.options(
        "/api/v1/health",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
    )
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_account_deletion_redacts_profile_and_revokes_access() -> None:
    client, token = login("delete-me")
    headers = {"Authorization": f"Bearer {token}"}
    deleted = client.delete("/api/v1/users/me", headers=headers)
    assert deleted.status_code == 204
    blocked = client.get("/api/v1/users/me", headers=headers)
    assert blocked.status_code == 400
    assert blocked.json()["error"]["code"] == "ACCOUNT_SUSPENDED"


def test_account_deletion_is_blocked_by_an_active_loan() -> None:
    borrower, borrower_token, _, _, _ = setup_loan()
    response = borrower.delete("/api/v1/users/me", headers={"Authorization": f"Bearer {borrower_token}"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "CONFLICT"
