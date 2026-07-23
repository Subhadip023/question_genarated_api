from pydantic import BaseModel, Field, model_validator


class DiagramCreate(BaseModel):
    type: int = Field(..., description="0 for question ref, 1 for question option ref")
    ref_id: int = Field(..., description="ID of the referred question or option")
    org_id: int = Field(..., description="Organization ID")
    user_id: int = Field(..., description="Creator user ID")
    path: str = Field(..., description="Diagram file path or URL")

    @model_validator(mode="after")
    def validate_type(cls, values):
        if values.type not in (0, 1):
            raise ValueError("type must be 0 or 1")
        return values


class DiagramResponse(BaseModel):
    id: int
    type: int
    ref_id: int
    org_id: int
    user_id: int
    path: str

    model_config = {"from_attributes": True}
