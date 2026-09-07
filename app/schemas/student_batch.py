from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StudentBatchCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    supervisor: int


class StudentBatchUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    supervisor: int | None = None
    is_active: bool | None = None


class StudentBatchResponse(BaseModel):
    id: int
    org_id: int
    name: str
    supervisor: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class BatchStudentResponse(BaseModel):
    id: int
    batch_id: int
    student_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BatchStudentUserResponse(BaseModel):
    id: int
    student_id: int
    name: str | None = None
    email: str | None = None


class AddBatchStudentsRequest(BaseModel):
    student_ids: list[int] = Field(..., min_length=1)