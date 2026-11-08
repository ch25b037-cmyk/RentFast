from datetime import timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.clock import now_utc
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User
from app.services.safety import sweep_overdue


def login(prefix: str) -> tuple[TestClient, str]:
    email = f"{prefix}+{uuid4().hex[:8]}@example.edu"
    client = TestClient(app)
    client.post("/api/v1/auth/otp/request", json={"email": email})
    response = client.post("/api/v1/auth/otp/verify", json={"email": email, "code": app.state.last_otp})
    return client, response.json()["access_token"]


def test_user_can_block_and_report_another_user() -> None:
    first, first_token = login("safety-first")
    second, second_token = login("safety-second")
    with SessionLocal() as db:
        users = list(db.scalars(select(User).where(User.email.like("safety-%@example.edu"))))
        assert len(users) >= 2
        second_user = next(user for user in users if user.email.startswith("safety-second"))
    headers = {"Authorization": f"Bearer {first_token}"}
    blocked = first.post("/api/v1/blocks", headers=headers, json={"user_id": second_user.id})
    assert blocked.status_code == 201
    assert first.get("/api/v1/blocks", headers=headers).json()[0]["blocked_id"] == second_user.id
    report = first.post("/api/v1/reports", headers=headers, json={"target_user_id": second_user.id, "reason": "harassment", "details": "Unwanted messages"})
    assert report.status_code == 201


def test_overdue_sweep_applies_penalty_once() -> None:
    with SessionLocal() as db:
        overdue = db.scalar(select(User).where(User.email.like("loan-borrower+%@example.edu")))
        assert overdue is not None
        before = overdue.trust_score
        from app.models.domain import Loan
        loan = db.scalar(select(Loan).where(Loan.borrower_id == overdue.id, Loan.status == "active"))
        if loan is None:
            return
        loan.due_at = now_utc() - timedelta(minutes=1)
        db.commit()
        assert sweep_overdue(db, now_utc()) == 1
        db.refresh(overdue)
        after = overdue.trust_score
        assert after == before - 8
        assert sweep_overdue(db, now_utc()) == 0
