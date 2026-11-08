from io import BytesIO
from uuid import uuid4

from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import select

from app.db.session import SessionLocal
from app.main import app
from app.models.domain import Category


def login(email: str) -> tuple[TestClient, str]:
    email = f"{email.split('@')[0]}+{uuid4().hex[:8]}@example.edu"
    client = TestClient(app)
    client.post("/api/v1/auth/otp/request", json={"email": email})
    response = client.post("/api/v1/auth/otp/verify", json={"email": email, "code": app.state.last_otp})
    return client, response.json()["access_token"]


def category_id() -> str:
    with SessionLocal() as db:
        category = db.scalar(select(Category).where(Category.slug == "calculators"))
        assert category is not None
        return category.id


def test_item_is_visible_only_to_its_owner() -> None:
    owner, owner_token = login("catalog-owner@example.edu")
    item = owner.post(
        "/api/v1/items",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"category_id": category_id(), "title": "Scientific calculator", "description": "Good for exams", "condition": "good", "value_tier": "low"},
    )
    assert item.status_code == 201

    stranger, stranger_token = login("catalog-stranger@example.edu")
    response = stranger.get(f"/api/v1/items/{item.json()['id']}", headers={"Authorization": f"Bearer {stranger_token}"})

    assert response.status_code == 404


def test_prohibited_category_cannot_create_item() -> None:
    with SessionLocal() as db:
        prohibited = db.scalar(select(Category).where(Category.slug == "weapons"))
        assert prohibited is not None
        prohibited_id = prohibited.id
    client, token = login("catalog-safe@example.edu")

    response = client.post(
        "/api/v1/items",
        headers={"Authorization": f"Bearer {token}"},
        json={"category_id": prohibited_id, "title": "Unsafe", "description": "No", "condition": "new", "value_tier": "high"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "PROHIBITED_ITEM"


def test_photo_upload_validates_content_and_serves_clean_image() -> None:
    client, token = login("catalog-photo@example.edu")
    headers = {"Authorization": f"Bearer {token}"}
    image = Image.new("RGBA", (1, 1), (30, 120, 90, 255))
    image_buffer = BytesIO()
    image.save(image_buffer, format="PNG")
    tiny_png = image_buffer.getvalue()
    uploaded = client.post("/api/v1/items/photos", headers=headers, files={"file": ("photo.png", tiny_png, "image/png")})
    assert uploaded.status_code == 201
    served = client.get(uploaded.json()["url"])
    assert served.status_code == 200
    assert served.headers["content-type"].startswith("image/png")

    rejected = client.post("/api/v1/items/photos", headers=headers, files={"file": ("photo.txt", b"not an image", "text/plain")})
    assert rejected.status_code == 400
    assert rejected.json()["error"]["code"] == "VALIDATION_ERROR"
