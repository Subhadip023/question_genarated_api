from pydantic import BaseModel
from typing import List

class QuestionSetCreate(BaseModel):

    name: str

    visibility: int = 0



class QuestionSetResponse(BaseModel):

    id: int
    name: str
    org_id: int
    user_id: int
    is_active: bool
    visibility: int


    class Config:
        from_attributes = True

class QuestionSetUpdate(BaseModel):
    name: str
    visibility: int
    is_active: int

class AddQuestionsRequest(BaseModel):
    question_ids: List[int]