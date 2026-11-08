"""The single authoritative loan state transition table."""

from app.core.clock import now_utc
from app.core.errors import DomainError
from app.models.domain import Loan, LoanEvent

LEGAL_TRANSITIONS = {
    "pending_handover": {"active", "cancelled"},
    "active": {"returned", "overdue", "disputed"},
    "overdue": {"returned", "disputed"},
    "returned": {"closed"},
    "disputed": {"closed"},
    "cancelled": set(),
    "closed": set(),
}


def transition(loan: Loan, target: str, actor_id: str | None, payload: dict, db) -> Loan:
    if target not in LEGAL_TRANSITIONS.get(loan.status, set()):
        raise DomainError("LOAN_INVALID_STATE", f"Cannot move a loan from {loan.status} to {target}.")
    loan.status = target
    if target == "active":
        loan.handed_over_at = now_utc()
    elif target == "returned":
        loan.returned_at = now_utc()
    elif target == "closed":
        loan.closed_at = now_utc()
    db.add(LoanEvent(loan_id=loan.id, actor_id=actor_id, type=f"{target}_transitioned", payload=payload))
    return loan
