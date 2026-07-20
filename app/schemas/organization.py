"""Pydantic schemas for organizations."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserResponse


class OrganizationAdminCreate(BaseModel):
    """Details for the first administrator of a new organization."""

    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=3, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=255)


class OrganizationCreate(BaseModel):
    """Schema for creating an organization."""

    name: str = Field(..., min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    phone_number: str | None = Field(default=None, min_length=5, max_length=30)
    is_active: bool = True
    admin: OrganizationAdminCreate


class OrganizationResponse(BaseModel):
    """Schema returned for an organization."""

    id: int
    name: str
    code: str
    location: str | None
    phone_number: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class OrganizationUpdate(BaseModel):
    """Fields an organization admin may update."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    location: str | None = Field(default=None, min_length=1, max_length=255)
    phone_number: str | None = Field(default=None, min_length=5, max_length=30)
    is_active: bool | None = None

    model_config = ConfigDict(extra="forbid")


class OrganizationCreateResponse(BaseModel):
    """New organization and its initial admin user."""

    organization: OrganizationResponse
    admin: UserResponse
