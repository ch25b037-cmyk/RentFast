"""Idempotent development seed for categories and curated meetup spots."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.domain import Category, MeetupSpot

CATEGORIES = [
    ("calculators", "Calculators", "calculator", 24, False),
    ("drafting-lab", "Drafting & lab gear", "flask", 72, False),
    ("electronics", "Electronics accessories", "plug", 48, False),
    ("formal-wear", "Formal wear", "shirt", 48, False),
    ("books-notes", "Books & notes", "book", 168, False),
    ("sports", "Sports gear", "trophy", 48, False),
    ("tools", "Tools", "wrench", 48, False),
    ("other", "Other", "box", 24, False),
    ("medicines", "Medicines", "ban", 0, True),
    ("alcohol-tobacco", "Alcohol/tobacco", "ban", 0, True),
    ("weapons", "Weapons", "ban", 0, True),
    ("exam-cheating", "Exam papers or cheating material", "ban", 0, True),
    ("id-documents", "ID cards/documents", "ban", 0, True),
    ("vehicles", "Vehicles", "ban", 0, True),
]
SPOTS = [
    ("Central Library Lobby", "Bright, staffed and easy to find.", "Ground floor beside the help desk."),
    ("Student Union Desk", "Public counter with campus staff nearby.", "Main entrance, next to reception."),
    ("Engineering Atrium", "Open atrium with cameras and seating.", "North wing, under the stairwell."),
    ("Science Block Cafe", "Busy cafe during class breaks.", "Inside the cafe, by the noticeboard."),
    ("Sports Complex Reception", "Staffed reception in a public building.", "Main lobby, near the equipment desk."),
    ("Admin Building Foyer", "Visible foyer with daytime foot traffic.", "Ground floor, opposite security."),
]


def main() -> None:
    with SessionLocal() as db:
        for slug, name, icon, hours, prohibited in CATEGORIES:
            if db.scalar(select(Category).where(Category.slug == slug)) is None:
                db.add(Category(slug=slug, name=name, icon=icon, max_loan_hours=hours, is_prohibited=prohibited))
        for name, description, hint in SPOTS:
            if db.scalar(select(MeetupSpot).where(MeetupSpot.name == name)) is None:
                db.add(MeetupSpot(name=name, description=description, location_hint=hint))
        db.commit()
    print("Seed complete")


if __name__ == "__main__":
    main()
