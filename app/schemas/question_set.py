from pydantic import BaseModel


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