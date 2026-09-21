"""Schemas for creating and returning test series."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SeriesQuestionInput(BaseModel):
    question_id: int
    marks: float | None = Field(default=None, ge=0)
    negative_marks: float | None = Field(default=None, ge=0)


class TestSeriesCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

    access_type: Literal[
        "invite_only",
        "public",
        "private"
    ] = "invite_only"

    teacher_group_id: int | None = None
    supervisor_id: int | None = None
    batch_id: int | None = None
    batch_ids: list[int] = Field(default_factory=list)
    student_ids: list[int] | None = None

    valid_until: datetime
    duration_seconds: int = Field(..., gt=0)

    questions: list[SeriesQuestionInput] = Field(default_factory=list)

    is_active: bool = True
    is_result_show: bool = False
    is_score_show: bool = False

    @field_validator("valid_until")
    @classmethod
    def validity_must_be_future_and_timezone_aware(
        cls,
        value: datetime
    ) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("valid_until must include a timezone")

        if value <= datetime.now(timezone.utc):
            raise ValueError("valid_until must be in the future")

        return value

    @field_validator("questions")
    @classmethod
    def questions_must_be_unique(
        cls,
        value: list[SeriesQuestionInput]
    ) -> list[SeriesQuestionInput]:
        question_ids = [question.question_id for question in value]

        if len(question_ids) != len(set(question_ids)):
            raise ValueError(
                "questions must not contain duplicate question_id"
            )

        return value


class TestSeriesResponse(BaseModel):
    id: int
    code: str | None
    invite_token: str | None = None
    access_type: str
    name: str

    org_id: int
    created_by: int
    teacher_group_id: int | None = None
    supervisor_id: int | None = None
    batch_id: int | None = None
    batch_ids: list[int] = Field(default_factory=list)
    student_ids: list[int] = Field(default_factory=list)

    valid_until: datetime
    duration_seconds: int

    is_active: bool
    is_result_show: bool
    is_score_show: bool

    questions: list[SeriesQuestionInput] = Field(default_factory=list)

    created_at: datetime
    updated_at: datetime
    attempt_count: int = 0


class TestSeriesUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)

    access_type: Literal[
        "invite_only",
        "public",
        "private"
    ] | None = None

    teacher_group_id: int | None = None
    supervisor_id: int | None = None
    batch_id: int | None = None
    batch_ids: list[int] | None = None
    student_ids: list[int] | None = None

    valid_until: datetime | None = None
    duration_seconds: int | None = Field(None, gt=0)

    questions: list[SeriesQuestionInput] | None = None

    is_active: bool | None = None
    is_result_show: bool | None = None
    is_score_show: bool | None = None

    regenerate_invite_token: bool | None = None

    @field_validator("valid_until")
    @classmethod
    def validity_must_be_future_and_timezone_aware(
        cls,
        value: datetime | None
    ) -> datetime | None:
        if value is None:
            return value

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("valid_until must include a timezone")

        if value <= datetime.now(timezone.utc):
            raise ValueError("valid_until must be in the future")

        return value

    @field_validator("questions")
    @classmethod
    def questions_must_be_unique(
        cls,
        value: list[SeriesQuestionInput] | None
    ) -> list[SeriesQuestionInput] | None:
        if value is None:
            return value

        question_ids = [question.question_id for question in value]

        if len(question_ids) != len(set(question_ids)):
            raise ValueError(
                "questions must not contain duplicate question_id"
            )

        return value


class TestSeriesResultItem(BaseModel):
    attempt_id: int
    user_id: int
    student_name: str
    student_email: str
    started_at: datetime
    submitted_at: datetime | None
    status: str | int
    score: float | None = None
    total_marks: float | None = None
    percentage: float | None = None


class TestSeriesResultsResponse(BaseModel):
    series_id: int
    series_name: str
    invite_token: str | None = None
    access_type: str | None = None
    is_result_show: bool
    result_file_key: str | None = None
    is_score_show: bool
    total_attempts: int
    completed_attempts: int
    average_score: float | None = None
    results: list[TestSeriesResultItem]