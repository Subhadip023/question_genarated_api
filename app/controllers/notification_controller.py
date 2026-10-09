import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.notification import Notification
from app.models.test_attempt import TestAttempt
from app.constants.attempt_status import AttemptStatus
from app.schemas.notification import NotificationListResponse, NotificationResponse, UnreadCountResponse

logger = logging.getLogger(__name__)


class NotificationController:
    """Controller for user and student notification management."""

    @staticmethod
    def get_notifications(
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
        db: Session = None,
    ) -> NotificationListResponse:
        query = db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read.is_(False))

        notifications = (
            query.order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

        unread_count = (
            db.query(func.count(Notification.id))
            .filter(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .scalar()
            or 0
        )

        return NotificationListResponse(
            items=[NotificationResponse.model_validate(n) for n in notifications],
            unread_count=unread_count,
        )

    @staticmethod
    def get_unread_count(user_id: int, db: Session) -> UnreadCountResponse:
        unread_count = (
            db.query(func.count(Notification.id))
            .filter(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .scalar()
            or 0
        )
        return UnreadCountResponse(unread_count=unread_count)

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int, db: Session) -> NotificationResponse | None:
        notification = (
            db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .first()
        )
        if not notification:
            return None

        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notification)
        return NotificationResponse.model_validate(notification)

    @staticmethod
    def mark_all_as_read(user_id: int, db: Session) -> dict:
        now = datetime.now(timezone.utc)
        db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        ).update(
            {"is_read": True, "read_at": now},
            synchronize_session=False,
        )
        db.commit()
        return {"message": "All notifications marked as read"}

    @staticmethod
    def notify_exam_result(
        user_id: int,
        series_id: int,
        series_name: str,
        attempt_id: int | None = None,
        db: Session = None,
    ) -> Notification:
        """Create an exam result notification for a student if not already notified."""
        try:
            # Check for existing notification to prevent duplicate alerts
            existing = (
                db.query(Notification)
                .filter(
                    Notification.user_id == user_id,
                    Notification.type == "exam_result",
                    Notification.reference_id == series_id,
                )
                .first()
            )
            if existing:
                return existing

            link = f"/student/attempts/{attempt_id}" if attempt_id else "/student/history"
            notification = Notification(
                user_id=user_id,
                title="Exam Result Out",
                message=f"[{series_name}] have result out",
                type="exam_result",
                reference_id=series_id,
                link=link,
                is_read=False,
                created_at=datetime.now(timezone.utc),
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            logger.info("Created exam result notification for user %s on series %s (%s)", user_id, series_id, series_name)
            return notification
        except Exception as e:
            db.rollback()
            logger.error("Failed to create exam result notification: %s", e)
            return None

    @staticmethod
    def notify_all_students_for_series(
        series_id: int,
        series_name: str,
        db: Session,
    ) -> int:
        """Notify all students who completed attempts on this series that results are out."""
        try:
            attempts = (
                db.query(TestAttempt)
                .filter(
                    TestAttempt.series_id == series_id,
                    TestAttempt.status != AttemptStatus.IN_PROGRESS,
                )
                .all()
            )

            notified_count = 0
            seen_users = set()
            for att in attempts:
                if att.user_id in seen_users:
                    continue
                seen_users.add(att.user_id)
                notif = NotificationController.notify_exam_result(
                    user_id=att.user_id,
                    series_id=series_id,
                    series_name=series_name,
                    attempt_id=att.id,
                    db=db,
                )
                if notif:
                    notified_count += 1

            logger.info("Sent exam result notifications to %d students for series %s", notified_count, series_name)
            return notified_count
        except Exception as e:
            logger.error("Failed to notify all students for series %s: %s", series_id, e)
            return 0
