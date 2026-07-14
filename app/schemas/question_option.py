from pydantic import BaseModel, Field


class OptionCreate(BaseModel):
    """Schema for adding one option to a question."""
    ans: str = Field(..., description="Answer text (can contain HTML)")
    is_correct: bool = Field(False, description="True for the correct answer")


class OptionResponse(BaseModel):
    """Schema for returning one option."""
    id: int
    q_id: int
    ans: str
    is_correct: bool

    model_config = {"from_attributes": True}
