"""Offers and in-app chat routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.offers import MessageCreate, MessageRead, OfferCreate, OfferRead
from app.services.offers import (
    accept_offer,
    add_message,
    create_offer,
    decline_offer,
    get_offer_for_party,
    list_messages,
    list_my_offers,
    list_offers_for_request,
    withdraw_offer,
)

router = APIRouter(tags=["offers"])


@router.post("/requests/{request_id}/offers", response_model=OfferRead, status_code=status.HTTP_201_CREATED)
def create(request_id: str, payload: OfferCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> OfferRead:
    return create_offer(db, request_id, user, payload.model_dump())


@router.get("/requests/{request_id}/offers", response_model=list[OfferRead])
def request_offers(request_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[OfferRead]:
    return list_offers_for_request(db, request_id, user)


@router.get("/offers/mine", response_model=list[OfferRead])
def mine(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[OfferRead]:
    return list_my_offers(db, user)


@router.post("/offers/{offer_id}/accept", response_model=dict)
def accept(offer_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    offer = get_offer_for_party(db, offer_id, user)
    loan = accept_offer(db, offer, user)
    return {"loan_id": loan.id, "status": loan.status}


@router.post("/offers/{offer_id}/decline", response_model=OfferRead)
def decline(offer_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> OfferRead:
    return decline_offer(db, get_offer_for_party(db, offer_id, user), user)


@router.post("/offers/{offer_id}/withdraw", response_model=OfferRead)
def withdraw(offer_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> OfferRead:
    return withdraw_offer(db, get_offer_for_party(db, offer_id, user), user)


@router.get("/offers/{offer_id}/messages", response_model=list[MessageRead])
def messages(offer_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[MessageRead]:
    offer = get_offer_for_party(db, offer_id, user)
    return list_messages(db, offer, user)


@router.post("/offers/{offer_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def message(offer_id: str, payload: MessageCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> MessageRead:
    offer = get_offer_for_party(db, offer_id, user)
    return add_message(db, offer, user, payload.body)
