"""Pydantic schemas for users."""

from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Schema for creating a user."""

    # Role 0 is reserved for the single superadmin and cannot be created here.
    role: int = Field(
        default=3,
        ge=1,
        le=3,
        description="1=admin, 2=teacher, 3=student",
    )
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)


class UserUpdate(BaseModel):
    """Schema for updating selected user fields."""

    role: int | None = Field(default=None, ge=1, le=3)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = Field(default=None, min_length=3, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=255)


class UserResponse(BaseModel):
    """Public user data; the password is intentionally excluded."""

    id: int
    role: int
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Credentials used to obtain an access token."""

    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)


class TokenResponse(BaseModel):
    """Bearer token returned after successful authentication."""

    message: str
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
