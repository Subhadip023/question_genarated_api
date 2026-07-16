"""Pydantic schemas for organizations."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserResponse


class OrganizationAdminCreate(BaseModel):
    """Details for the first administrator of a new organization."""

    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)


class OrganizationCreate(BaseModel):
    """Schema for creating an organization."""

    name: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True
    admin: OrganizationAdminCreate


class OrganizationResponse(BaseModel):
    """Schema returned for an organization."""

    id: int
    name: str
    is_active: bool

    model_config = {"from_attributes": True}


class OrganizationUpdate(BaseModel):
    """Admin-editable organization fields; is_active is intentionally excluded."""

    name: str | None = Field(default=None, min_length=1, max_length=255)

    model_config = ConfigDict(extra="forbid")


class OrganizationCreateResponse(BaseModel):
    """New organization and its initial admin user."""

    organization: OrganizationResponse
    admin: UserResponse
