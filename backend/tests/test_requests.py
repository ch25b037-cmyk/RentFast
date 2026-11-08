from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.clock import now_utc
from app.db.session import SessionLocal
from app.main import app
from app.models.domain import Category


def login(email: str) -> tuple[TestClient, str]:
    email = f"{email.split('@')[0]}+{uuid4().hex[:8]}@example.edu"
    client = TestClient(app)
    client.post("/api/v1/auth/otp/request", json={"email": email})
    response = client.post("/api/v1/auth/otp/verify", json={"email": email, "code": app.state.last_otp})
    return client, response.json()["access_token"]


def category_id() -> str:
    with SessionLocal() as db:
        category = db.scalar(select(Category).where(Category.slug == "calculators"))
        assert category is not None
        return category.id


def request_body() -> dict:
    start = now_utc() + timedelta(hours=2)
    return {"category_id": category_id(), "title": "Need a calculator", "description": "For a short exam window", "needed_from": start.isoformat(), "needed_until": (start + timedelta(hours=2)).isoformat()}


def test_request_can_be_created_and_listed() -> None:
    client, token = login("requester@example.edu")
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post("/api/v1/requests", headers=headers, json=request_body())
    assert created.status_code == 201
    listed = client.get("/api/v1/requests?mine=true", headers=headers)

    assert listed.status_code == 200
    assert any(item["id"] == created.json()["id"] for item in listed.json()["items"])


def test_request_window_cannot_exceed_category_limit() -> None:
    client, token = login("window-check@example.edu")
    body = request_body()
    body["needed_until"] = (datetime.fromisoformat(body["needed_from"]) + timedelta(hours=25)).isoformat()

    response = client.post("/api/v1/requests", headers={"Authorization": f"Bearer {token}"}, json=body)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_member_can_list_all_of_their_requests() -> None:
    client, token = login("requests-all")
    response = client.get("/api/v1/requests?status=all&mine=true", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["total"] >= 0
