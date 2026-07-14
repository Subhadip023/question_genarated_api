from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.question_option import OptionResponse


class QuestionCreate(BaseModel):
    """Schema for creating a new question."""
    question: str = Field(..., description="HTML content of the question")
    is_active: bool = Field(True, description="Whether the question is active")


class QuestionResponse(BaseModel):
    """Schema for returning a question with its options."""
    id: int
    question: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    options: list[OptionResponse] = []  # nested options from the relationship

    model_config = {"from_attributes": True}
