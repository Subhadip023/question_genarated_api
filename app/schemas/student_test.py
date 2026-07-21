"""Student-facing test and attempt schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


class AvailableSeriesResponse(BaseModel):
    id: int
    name: str
    org_id: int
    valid_until: datetime
    duration_seconds: int
    question_count: int
    topics: list[str] = Field(default_factory=list)


class PaginatedAvailableSeriesResponse(BaseModel):
    items: list[AvailableSeriesResponse]
    total: int
    page: int
    limit: int
    total_pages: int




class StartAttemptRequest(BaseModel):
    series_id: int | None = None
    invite_token: str | None = Field(default=None, min_length=8, max_length=255)

    @model_validator(mode="after")
    def require_series_or_code(self):
        if (self.series_id is None) == (self.invite_token is None):
            raise ValueError(
                "Provide either series_id for a public test or invite_token for an invite-only test"
            )
        return self


class AttemptOptionResponse(BaseModel):
    id: int
    ans: str


class AttemptQuestionResponse(BaseModel):
    id: int
    original_question_id: int
    position: int
    question: str
    marks: Decimal
    options: list[AttemptOptionResponse]
    selected_option_id: int | None
    correct_option_id: int | None = None


class AttemptResponse(BaseModel):
    id: int
    series_id: int
    series_name: str
    started_at: datetime
    expires_at: datetime
    submitted_at: datetime | None
    status: str
    score: Decimal
    total_marks: Decimal
    questions: list[AttemptQuestionResponse]


class SaveAnswerRequest(BaseModel):
    selected_option_id: int


class AttemptHistoryResponse(BaseModel):
    id: int
    series_id: int
    series_name: str
    started_at: datetime
    expires_at: datetime
    submitted_at: datetime | None
    status: str
    score: Decimal
    total_marks: Decimal
