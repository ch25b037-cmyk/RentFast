from datetime import timedelta
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


def create_request(client: TestClient, token: str) -> str:
    with SessionLocal() as db:
        category = db.scalar(select(Category).where(Category.slug == "calculators"))
        assert category is not None
    start = now_utc() + timedelta(hours=2)
    response = client.post("/api/v1/requests", headers={"Authorization": f"Bearer {token}"}, json={"category_id": category.id, "title": "Need a shared calculator", "description": "For one class", "needed_from": start.isoformat(), "needed_until": (start + timedelta(hours=2)).isoformat()})
    assert response.status_code == 201
    return response.json()["id"]


def test_offer_acceptance_creates_loan_and_masks_contacts() -> None:
    borrower, borrower_token = login("offer-borrower@example.edu")
    lender, lender_token = login("offer-lender@example.edu")
    request_id = create_request(borrower, borrower_token)
    borrower_headers = {"Authorization": f"Bearer {borrower_token}"}
    lender_headers = {"Authorization": f"Bearer {lender_token}"}

    offer = lender.post(f"/api/v1/requests/{request_id}/offers", headers=lender_headers, json={"message": "I can lend this. email me at lender@example.edu"})
    assert offer.status_code == 201
    offer_id = offer.json()["id"]
    chat = lender.get(f"/api/v1/offers/{offer_id}/messages", headers=lender_headers)
    assert chat.status_code == 200
    sent = lender.post(f"/api/v1/offers/{offer_id}/messages", headers=lender_headers, json={"body": "Call +91 98765 43210"})
    assert sent.status_code == 201
    assert sent.json()["masked"] is True
    assert "98765" not in sent.json()["body"]

    accepted = borrower.post(f"/api/v1/offers/{offer_id}/accept", headers=borrower_headers)

    assert accepted.status_code == 200
    assert accepted.json()["status"] == "pending_handover"
    mine = borrower.get("/api/v1/requests?status=all&mine=true", headers=borrower_headers)
    assert mine.status_code == 200
    matched = next(item for item in mine.json()["items"] if item["id"] == request_id)
    assert matched["status"] == "matched"
    assert matched["loan_id"] == accepted.json()["loan_id"]
    notices = lender.get("/api/v1/notifications?unread=true", headers=lender_headers)
    assert notices.status_code == 200
    assert any(item["type"] == "offer_accepted" for item in notices.json()["items"])
