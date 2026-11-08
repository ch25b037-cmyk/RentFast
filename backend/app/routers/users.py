"""User profile routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.user import PublicUserResponse, UserUpdate
from app.services.user import delete_account, get_current, trust_tier, update_profile

router = APIRouter(prefix="/users", tags=["users"])


def response(user: User) -> UserResponse:
    return UserResponse.model_validate({**user.as_dict(), "trust_tier": trust_tier(user.trust_score)})


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)) -> UserResponse:
    return response(user)


@router.patch("/me", response_model=UserResponse)
def update_me(payload: UserUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> UserResponse:
    return response(update_profile(db, user, payload.model_dump(exclude_unset=True)))


@router.get("/{user_id}", response_model=PublicUserResponse)
def public_profile(user_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> PublicUserResponse:
    target = get_current(db, user_id)
    return PublicUserResponse(id=target.id, display_name=target.display_name, avatar_url=target.avatar_url, trust_score=target.trust_score, trust_tier=trust_tier(target.trust_score), completed_loans=target.completed_loans)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> None:
    delete_account(db, user)
