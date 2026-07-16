from sqlalchemy.orm import Session
from app.models.topic import Topic
from app.models.organization_user import OrganizationUser
from app.schemas.topic import TopicCreate, TopicUpdate, TopicResponse


class TopicPermissionError(Exception):
    """Raised when user has insufficient permissions to manage topics."""


class TopicController:
    """Controller responsible for handling topic-related business logic."""

    @staticmethod
    def create_topic(
        data: TopicCreate,
        user_id: int,
        user_role: int,
        db: Session,
    ) -> TopicResponse:
        """Create a new topic for the user's organization or global if superadmin."""
        if user_role not in (0, 1, 2):
            raise TopicPermissionError("Only roles 0, 1, and 2 can create topics")

        if user_role == 0:
            org_id = 0
        else:
            membership = (
                db.query(OrganizationUser)
                .filter(OrganizationUser.user_id == user_id)
                .order_by(OrganizationUser.org_id)
                .first()
            )
            if membership is None:
                raise TopicPermissionError("User does not belong to an organization")
            org_id = membership.org_id

        topic = Topic(
            name=data.name,
            color=data.color,
            is_active=data.is_active,
            org_id=org_id,
        )

        try:
            db.add(topic)
            db.commit()
            db.refresh(topic)
        except Exception:
            db.rollback()
            raise

        return TopicResponse.model_validate(topic)

    @staticmethod
    def get_all_topics(
        user_id: int,
        user_role: int,
        db: Session,
    ) -> list[TopicResponse]:
        """Fetch all topics visible to the authenticated user."""
        query = db.query(Topic)

        if user_role == 0:
            # Superadmin can view all topics
            pass
        elif user_role in (1, 2, 3):
            # Fetch topics belonging to user's org + global topics (org_id = 0)
            membership = (
                db.query(OrganizationUser)
                .filter(OrganizationUser.user_id == user_id)
                .order_by(OrganizationUser.org_id)
                .first()
            )
            org_id = membership.org_id if membership else -1
            query = query.filter((Topic.org_id == org_id) | (Topic.org_id == 0))
        else:
            return []

        topics = query.filter(Topic.is_active.is_(True)).all()
        return [TopicResponse.model_validate(t) for t in topics]

    @staticmethod
    def get_topic(
        topic_id: int,
        user_id: int,
        user_role: int,
        db: Session,
    ) -> TopicResponse | None:
        """Fetch a single topic by ID with visibility checks."""
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            return None

        # Check visibility
        if user_role != 0:
            membership = (
                db.query(OrganizationUser)
                .filter(OrganizationUser.user_id == user_id)
                .order_by(OrganizationUser.org_id)
                .first()
            )
            user_org_id = membership.org_id if membership else -1
            if topic.org_id != 0 and topic.org_id != user_org_id:
                return None

        return TopicResponse.model_validate(topic)

    @staticmethod
    def update_topic(
        topic_id: int,
        data: TopicUpdate,
        user_id: int,
        user_role: int,
        db: Session,
    ) -> TopicResponse | None:
        """Update a topic (only same org or superadmin)."""
        if user_role not in (0, 1, 2):
            raise TopicPermissionError("Only roles 0, 1, and 2 can update topics")

        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            return None

        # Verify permissions
        if user_role != 0:
            membership = (
                db.query(OrganizationUser)
                .filter(OrganizationUser.user_id == user_id)
                .order_by(OrganizationUser.org_id)
                .first()
            )
            user_org_id = membership.org_id if membership else -1
            if topic.org_id != user_org_id:
                raise TopicPermissionError("You can only update topics belonging to your organization")

        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            if value is not None:
                setattr(topic, field, value)

        try:
            db.commit()
            db.refresh(topic)
        except Exception:
            db.rollback()
            raise

        return TopicResponse.model_validate(topic)

    @staticmethod
    def delete_topic(
        topic_id: int,
        user_id: int,
        user_role: int,
        db: Session,
    ) -> bool:
        """Delete a topic (only same org or superadmin)."""
        if user_role not in (0, 1, 2):
            raise TopicPermissionError("Only roles 0, 1, and 2 can delete topics")

        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            return False

        # Verify permissions
        if user_role != 0:
            membership = (
                db.query(OrganizationUser)
                .filter(OrganizationUser.user_id == user_id)
                .order_by(OrganizationUser.org_id)
                .first()
            )
            user_org_id = membership.org_id if membership else -1
            if topic.org_id != user_org_id:
                raise TopicPermissionError("You can only delete topics belonging to your organization")

        try:
            db.delete(topic)
            db.commit()
        except Exception:
            db.rollback()
            raise

        return True
