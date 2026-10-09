from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.controllers.notification_controller import NotificationController
from app.dependencies.db import get_db
from app.schemas.notification import NotificationListResponse, NotificationResponse, UnreadCountResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse, summary="Get notifications for current user")
def get_notifications(
    request: Request,
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> NotificationListResponse:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return NotificationController.get_notifications(
        user_id=user_id,
        unread_only=unread_only,
        limit=limit,
        db=db,
    )


@router.get("/unread-count", response_model=UnreadCountResponse, summary="Get unread notification count")
def get_unread_count(
    request: Request,
    db: Session = Depends(get_db),
) -> UnreadCountResponse:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return NotificationController.get_unread_count(user_id=user_id, db=db)


@router.patch("/{notification_id}/read", response_model=NotificationResponse, summary="Mark notification as read")
def mark_as_read(
    notification_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> NotificationResponse:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    result = NotificationController.mark_as_read(
        notification_id=notification_id,
        user_id=user_id,
        db=db,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Notification not found")
    return result


@router.post("/read-all", summary="Mark all notifications as read")
def mark_all_as_read(
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return NotificationController.mark_all_as_read(user_id=user_id, db=db)
