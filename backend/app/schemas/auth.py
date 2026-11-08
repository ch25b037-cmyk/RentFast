"""Authentication request and response models."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    display_name: str
    department: str | None
    hostel: str | None
    avatar_url: str | None
    role: str
    status: str
    trust_score: int
    trust_tier: str


TokenResponse.model_rebuild()
