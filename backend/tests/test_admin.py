from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.user import User


def login(email: str) -> tuple[TestClient, str]:
    client = TestClient(app)
    client.post("/api/v1/auth/otp/request", json={"email": email})
    response = client.post("/api/v1/auth/otp/verify", json={"email": email, "code": app.state.last_otp})
    return client, response.json()["access_token"]


def test_non_admin_cannot_access_admin_routes() -> None:
    client, token = login(f"admin-test+{uuid4().hex[:8]}@example.edu")

    response = client.get("/api/v1/admin/reports", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_admin_can_view_audit_log() -> None:
    email = f"admin+{uuid4().hex[:8]}@example.edu"
    with SessionLocal() as db:
        user = db.scalar(__import__("sqlalchemy", fromlist=["select"]).select(User).where(User.email == email))
        if user is None:
            user = User(email=email, role="admin", email_verified_at=__import__("app.core.clock", fromlist=["now_utc"]).now_utc())
            db.add(user)
            db.commit()
    client, token = login(email)

    response = client.get("/api/v1/admin/audit-log", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
