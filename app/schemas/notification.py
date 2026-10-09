from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    reference_id: int | None = None
    link: str | None = None
    is_read: bool
    created_at: datetime
    read_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    unread_count: int


class UnreadCountResponse(BaseModel):
    unread_count: int
