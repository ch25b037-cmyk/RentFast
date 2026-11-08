"""Catalog, curated meetup and item services."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import DomainError, NotFoundError
from app.models.domain import Category, Item, MeetupSpot


def list_categories(db: Session) -> list[Category]:
    return list(db.scalars(select(Category).where(Category.is_prohibited.is_(False)).order_by(Category.name)))


def list_meetup_spots(db: Session) -> list[MeetupSpot]:
    return list(db.scalars(select(MeetupSpot).where(MeetupSpot.is_active.is_(True)).order_by(MeetupSpot.name)))


def list_items(db: Session, owner_id: str, limit: int, offset: int) -> tuple[list[Item], int]:
    query = select(Item).where(Item.owner_id == owner_id, Item.deleted_at.is_(None)).order_by(Item.created_at.desc())
    all_items = list(db.scalars(query))
    return all_items[offset : offset + limit], len(all_items)


def create_item(db: Session, owner_id: str, values: dict) -> Item:
    category = db.get(Category, values["category_id"])
    if category is None:
        raise NotFoundError("Category not found")
    if category.is_prohibited:
        raise DomainError("PROHIBITED_ITEM", "This category cannot be lent on CampusLend.")
    item = Item(owner_id=owner_id, **values)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_owned_item(db: Session, owner_id: str, item_id: str) -> Item:
    item = db.scalar(select(Item).where(Item.id == item_id, Item.owner_id == owner_id, Item.deleted_at.is_(None)))
    if item is None:
        raise NotFoundError()
    return item


def update_item(db: Session, item: Item, values: dict) -> Item:
    for key, value in values.items():
        if value is not None:
            setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item: Item) -> None:
    item.deleted_at = datetime.now(UTC)
    item.is_available = False
    db.commit()
