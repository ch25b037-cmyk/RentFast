from fastapi.testclient import TestClient

from app.main import app


def test_non_allowlisted_domain_is_rejected() -> None:
    response = TestClient(app).post("/api/v1/auth/otp/request", json={"email": "student@outside.com"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "EMAIL_DOMAIN_NOT_ALLOWED"


def test_otp_login_creates_user_and_me_profile() -> None:
    client = TestClient(app)
    email = "m1-student@example.edu"

    request = client.post("/api/v1/auth/otp/request", json={"email": email})
    assert request.status_code == 202
    code = app.state.last_otp

    verified = client.post("/api/v1/auth/otp/verify", json={"email": email, "code": code})
    assert verified.status_code == 200
    token = verified.json()["access_token"]
    assert "email" in verified.json()["user"]

    me = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == email
    assert "hostel" in me.json()


def test_invalid_otp_is_rejected() -> None:
    client = TestClient(app)
    email = "m1-invalid@example.edu"
    client.post("/api/v1/auth/otp/request", json={"email": email})

    response = client.post("/api/v1/auth/otp/verify", json={"email": email, "code": "000000"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "OTP_INVALID"


def test_profile_is_not_visible_without_access_token() -> None:
    response = TestClient(app).get("/api/v1/users/me")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"
