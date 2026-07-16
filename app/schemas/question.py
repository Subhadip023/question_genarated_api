from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from decimal import Decimal
from app.schemas.question_option import OptionResponse, OptionCreate


class QuestionCreate(BaseModel):
    """Schema for creating a new question."""
    question: str = Field(..., description="HTML content of the question")
    is_global: bool = Field(True, description="Whether the question is global")
    marks: Decimal = Field(Decimal("1.00"), description="Marks for the question")
    is_active: bool = Field(True, description="Whether the question is active")
    options: list[OptionCreate] = Field(
        default_factory=list,
        description="Options for the question",
    )


class BulkQuestionCreate(QuestionCreate):
    """One question in a bulk-create request."""

    options: list[OptionCreate] = Field(
        ...,
        min_length=2,
        description="Answer options; exactly one must be marked as correct",
    )

    @model_validator(mode="after")
    def exactly_one_option_must_be_correct(self):
        if sum(option.is_correct for option in self.options) != 1:
            raise ValueError("exactly one option must have is_correct=true")
        return self


class QuestionUpdate(BaseModel):
    """Schema for partially updating a question."""
    question: str | None = Field(None, description="HTML content of the question")
    is_global: bool | None = Field(None, description="Whether the question is global")
    marks: Decimal | None = Field(None, description="Marks for the question")
    is_active: bool | None = Field(None, description="Whether the question is active")
    options: list[OptionCreate] | None = Field(
        None,
        description="Replacement options for the question",
    )


class QuestionResponse(BaseModel):
    """Schema for returning a question with its options."""
    id: int
    question: str
    organization_id: int
    user_id: int
    is_global: bool
    marks: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
    options: list[OptionResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}
