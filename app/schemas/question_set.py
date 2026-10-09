from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class QuestionSetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    visibility: int = 0  # 0 = Organization only, 1 = Public

class QuestionSetResponse(BaseModel):
    id: int
    name: str
    org_id: int | None = None
    user_id: int
    is_active: bool
    visibility: int
    question_count: int = 0

    class Config:
        from_attributes = True

class QuestionSetUpdate(BaseModel):
    name: Optional[str] = None
    visibility: Optional[int] = None
    is_active: Optional[bool] = None

class AddQuestionsRequest(BaseModel):
    question_ids: List[int]

class ConvertToTestSeriesRequest(BaseModel):
    name: Optional[str] = None
    duration_minutes: int = 60
    valid_until: datetime
    access_type: str = "invite_only"  # public | invite_only | private