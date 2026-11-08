"""Reports and block-list routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.safety import BlockCreate, BlockRead, ReportCreate, ReportRead
from app.services.safety import block_user, create_report, list_blocks, unblock_user

router = APIRouter(tags=["safety"])


@router.post("/reports", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
def report(payload: ReportCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ReportRead:
    return create_report(db, user, payload.model_dump())


@router.post("/blocks", response_model=BlockRead, status_code=status.HTTP_201_CREATED)
def block(payload: BlockCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> BlockRead:
    return block_user(db, user, payload.user_id)


@router.delete("/blocks/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def unblock(user_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> None:
    unblock_user(db, user, user_id)


@router.get("/blocks", response_model=list[BlockRead])
def blocks(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[BlockRead]:
    return list_blocks(db, user)
