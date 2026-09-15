from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnswerKeyResponse(BaseModel):
    id: int
    test_series_id: int
    path: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)