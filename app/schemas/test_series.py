"""Schemas for creating and returning test series."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TestSeriesCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    access_type: Literal["invite_only", "public"] = "invite_only"
    valid_until: datetime
    duration_seconds: int = Field(..., gt=0)
    question_ids: list[int] = Field(..., min_length=1)
    is_active: bool = True

    @field_validator("valid_until")
    @classmethod
    def validity_must_be_future_and_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("valid_until must include a timezone")
        if value <= datetime.now(timezone.utc):
            raise ValueError("valid_until must be in the future")
        return value

    @field_validator("question_ids")
    @classmethod
    def question_ids_must_be_unique(cls, value: list[int]) -> list[int]:
        if len(value) != len(set(value)):
            raise ValueError("question_ids must not contain duplicates")
        return value


class TestSeriesResponse(BaseModel):
    id: int
    code: str | None
    invite_token: str | None = None
    access_type: Literal["invite_only", "public"]
    name: str
    org_id: int
    created_by: int
    valid_until: datetime
    duration_seconds: int
    is_active: bool
    question_ids: list[int]
    created_at: datetime
    updated_at: datetime


class TestSeriesUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    access_type: Literal["invite_only", "public"] | None = None
    valid_until: datetime | None = None
    duration_seconds: int | None = Field(None, gt=0)
    question_ids: list[int] | None = Field(None, min_length=1)
    is_active: bool | None = None

    @field_validator("valid_until")
    @classmethod
    def validity_must_be_future_and_timezone_aware(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return value
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("valid_until must include a timezone")
        if value <= datetime.now(timezone.utc):
            raise ValueError("valid_until must be in the future")
        return value

    @field_validator("question_ids")
    @classmethod
    def question_ids_must_be_unique(cls, value: list[int] | None) -> list[int] | None:
        if value is None:
            return value
        if len(value) != len(set(value)):
            raise ValueError("question_ids must not contain duplicates")
        return value

