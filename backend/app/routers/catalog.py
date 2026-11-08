"""Categories, meetup spots and inventory routes."""

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.catalog import (
    CategoryRead,
    ItemCreate,
    ItemPage,
    ItemRead,
    ItemUpdate,
    MeetupSpotRead,
    UploadRead,
)
from app.services.catalog import (
    create_item,
    delete_item,
    get_owned_item,
    list_categories,
    list_items,
    list_meetup_spots,
    update_item,
)
from app.services.uploads import save_image

router = APIRouter(tags=["catalog"])


@router.get("/categories", response_model=list[CategoryRead])
def categories(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list:
    return list_categories(db)


@router.get("/meetup-spots", response_model=list[MeetupSpotRead])
def meetup_spots(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list:
    return list_meetup_spots(db)


@router.get("/items", response_model=ItemPage)
def items(limit: int = 20, offset: int = 0, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ItemPage:
    limit = min(max(limit, 1), 50)
    values, total = list_items(db, user.id, limit, max(offset, 0))
    return ItemPage(items=values, total=total, limit=limit, offset=max(offset, 0))


@router.post("/items/photos", response_model=UploadRead, status_code=status.HTTP_201_CREATED)
async def upload_photo(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> UploadRead:
    return UploadRead(url=await save_image(db, user, file))


@router.post("/items", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create(payload: ItemCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ItemRead:
    return create_item(db, user.id, payload.model_dump())


@router.get("/items/{item_id}", response_model=ItemRead)
def get(item_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ItemRead:
    return get_owned_item(db, user.id, item_id)


@router.patch("/items/{item_id}", response_model=ItemRead)
def update(item_id: str, payload: ItemUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ItemRead:
    return update_item(db, get_owned_item(db, user.id, item_id), payload.model_dump(exclude_unset=True))


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(item_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> None:
    delete_item(db, get_owned_item(db, user.id, item_id))
