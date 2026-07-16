from pydantic import BaseModel, Field
from datetime import datetime


class TopicCreate(BaseModel):
    """Schema for creating a new topic."""
    name: str = Field(..., min_length=1, max_length=255, description="Name of the topic")
    color: str = Field("#000000", max_length=50, description="Hex color or color name")
    is_active: bool = Field(True, description="Whether the topic is active")


class TopicUpdate(BaseModel):
    """Schema for partially updating a topic."""
    name: str | None = Field(None, min_length=1, max_length=255)
    color: str | None = Field(None, max_length=50)
    is_active: bool | None = Field(None)


class TopicResponse(BaseModel):
    """Schema for returning a topic."""
    id: int
    org_id: int
    name: str
    color: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
