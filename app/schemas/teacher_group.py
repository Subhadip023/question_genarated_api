"""Pydantic schemas for teacher groups and group teachers."""

from datetime import datetime
from pydantic import BaseModel, Field


class TeacherUserSummary(BaseModel):
    """Minimal user payload for supervisor and teacher fields."""

    id: int
    name: str
    email: str
    role: int

    model_config = {"from_attributes": True}


class GroupTeacherResponse(BaseModel):
    """Response schema for individual group teacher association."""

    id: int
    group_id: int
    teacher_id: int
    created_at: datetime
    teacher: TeacherUserSummary | None = None

    model_config = {"from_attributes": True}


class TeacherGroupCreate(BaseModel):
    """Request payload for creating a teacher group."""

    name: str = Field(..., min_length=1, max_length=255, description="Name of the teacher group")
    supervisor: int = Field(..., description="User ID of the supervisor (teacher or admin)")
    org_id: int | None = Field(
        default=None, description="Organization ID (optional, auto-filled for non-superadmin)"
    )
    teacher_ids: list[int] = Field(
        default_factory=list, description="List of teacher user IDs to assign to the group"
    )
    is_active: bool = Field(default=True, description="Active status of the group")


class TeacherGroupUpdate(BaseModel):
    """Request payload for updating a teacher group."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    supervisor: int | None = Field(default=None, description="User ID of the supervisor")
    teacher_ids: list[int] | None = Field(default=None, description="List of teacher user IDs")
    is_active: bool | None = Field(default=None)


class TeacherGroupResponse(BaseModel):
    """Response schema for teacher group details."""

    id: int
    org_id: int
    created_by: int
    name: str
    supervisor: int
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    creator: TeacherUserSummary | None = None
    supervisor_user: TeacherUserSummary | None = None
    teachers: list[TeacherUserSummary] = Field(default_factory=list)

    model_config = {"from_attributes": True}
