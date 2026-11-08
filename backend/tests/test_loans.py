from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.clock import now_utc
from app.core.errors import DomainError
from app.db.session import SessionLocal
from app.main import app
from app.models.domain import Category, Loan, LoanEvent, MeetupSpot
from app.services.loan_state import transition
from app.services.loans import auto_accept_return_claims


def login(email: str) -> tuple[TestClient, str]:
    email = f"{email.split('@')[0]}+{uuid4().hex[:8]}@example.edu"
    client = TestClient(app)
    client.post("/api/v1/auth/otp/request", json={"email": email})
    response = client.post("/api/v1/auth/otp/verify", json={"email": email, "code": app.state.last_otp})
    return client, response.json()["access_token"]


def setup_loan() -> tuple[TestClient, str, TestClient, str, str]:
    borrower, borrower_token = login("loan-borrower@example.edu")
    lender, lender_token = login("loan-lender@example.edu")
    with SessionLocal() as db:
        category = db.scalar(select(Category).where(Category.slug == "calculators"))
        spot = db.scalar(select(MeetupSpot).where(MeetupSpot.is_active.is_(True)))
        assert category and spot
    start = now_utc() + timedelta(hours=2)
    request = borrower.post("/api/v1/requests", headers={"Authorization": f"Bearer {borrower_token}"}, json={"category_id": category.id, "title": "Loan lifecycle test", "description": "A test request", "needed_from": start.isoformat(), "needed_until": (start + timedelta(hours=2)).isoformat(), "preferred_spot_id": spot.id})
    offer = lender.post(f"/api/v1/requests/{request.json()['id']}/offers", headers={"Authorization": f"Bearer {lender_token}"}, json={"message": "I can help"})
    accepted = borrower.post(f"/api/v1/offers/{offer.json()['id']}/accept", headers={"Authorization": f"Bearer {borrower_token}"})
    return borrower, borrower_token, lender, lender_token, accepted.json()["loan_id"]


def test_codes_require_both_agreement_and_spot_then_complete_happy_path() -> None:
    borrower, borrower_token, lender, lender_token, loan_id = setup_loan()
    borrower_headers = {"Authorization": f"Bearer {borrower_token}"}
    lender_headers = {"Authorization": f"Bearer {lender_token}"}

    blocked = borrower.post(f"/api/v1/loans/{loan_id}/codes/handover", headers=borrower_headers)
    assert blocked.json()["error"]["code"] == "AGREEMENT_REQUIRED"
    for headers in (borrower_headers, lender_headers):
        agreed = borrower.post(f"/api/v1/loans/{loan_id}/agree", headers=headers, json={"agreement_version": 1}) if headers is borrower_headers else lender.post(f"/api/v1/loans/{loan_id}/agree", headers=headers, json={"agreement_version": 1})
        assert agreed.status_code == 200
    with SessionLocal() as db:
        spot = db.scalar(select(MeetupSpot).where(MeetupSpot.is_active.is_(True)))
        assert spot
    scheduled = now_utc() + timedelta(hours=1)
    assert borrower.post(f"/api/v1/loans/{loan_id}/spot", headers=borrower_headers, json={"spot_id": spot.id, "scheduled_start": scheduled.isoformat()}).status_code == 200
    code_response = borrower.post(f"/api/v1/loans/{loan_id}/codes/handover", headers=borrower_headers)
    assert code_response.status_code == 200
    code = code_response.json()["code"]
    wrong_role = borrower.post(f"/api/v1/loans/{loan_id}/confirm-handover", headers=borrower_headers, json={"code": code})
    assert wrong_role.json()["error"]["code"] == "FORBIDDEN"
    active = lender.post(f"/api/v1/loans/{loan_id}/confirm-handover", headers=lender_headers, json={"code": code})
    assert active.json()["status"] == "active"
    return_code = lender.post(f"/api/v1/loans/{loan_id}/codes/return", headers=lender_headers).json()["code"]
    returned = borrower.post(f"/api/v1/loans/{loan_id}/confirm-return", headers=borrower_headers, json={"code": return_code})
    assert returned.json()["status"] == "returned"


def test_illegal_loan_transition_is_rejected() -> None:
    borrower, borrower_token, lender, lender_token, loan_id = setup_loan()
    with SessionLocal() as db:
        from app.models.domain import Loan
        loan = db.get(Loan, loan_id)
        assert loan
        with pytest.raises(DomainError, match="Cannot move"):
            transition(loan, "closed", loan.borrower_id, {}, db)


def test_return_claim_auto_accepts_after_deadline() -> None:
    borrower, borrower_token, _, _, loan_id = setup_loan()
    with SessionLocal() as db:
        loan = db.get(Loan, loan_id)
        assert loan
        transition(loan, "active", loan.borrower_id, {}, db)
        db.commit()

    headers = {"Authorization": f"Bearer {borrower_token}"}
    assert borrower.post(f"/api/v1/loans/{loan_id}/return-claim", headers=headers).status_code == 200
    with SessionLocal() as db:
        claim = db.scalar(select(LoanEvent).where(LoanEvent.loan_id == loan_id, LoanEvent.type == "return_claimed"))
        loan = db.get(Loan, loan_id)
        assert claim and loan
        claim.payload = {"auto_accept_at": (now_utc() - timedelta(minutes=1)).isoformat()}
        db.commit()
        assert auto_accept_return_claims(db) == 1
        assert loan.status == "returned"
