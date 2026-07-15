from pydantic import BaseModel, Field
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


class QuestionResponse(BaseModel):
    """Schema for returning a question with its options."""
    id: int
    question: str
    is_global: bool
    marks: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
    options: list[OptionResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}
