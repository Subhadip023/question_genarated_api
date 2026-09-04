"""Business logic for teacher groups management."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.models.group_teacher import GroupTeacher
from app.models.organization_user import OrganizationUser
from app.models.teacher_group import TeacherGroup
from app.models.user import User
from app.schemas.teacher_group import (
    TeacherGroupCreate,
    TeacherGroupResponse,
    TeacherGroupUpdate,
    TeacherUserSummary,
)


class TeacherGroupPermissionError(Exception):
    """Raised when user has insufficient permissions to manage teacher groups."""


class TeacherGroupValidationError(Exception):
    """Raised when request payload fails business validation (e.g. invalid supervisor)."""


class TeacherGroupController:
    """Controller for teacher groups and group teachers CRUD operation business logic."""

    @staticmethod
    def _get_user_org_id(user_id: int, user_role: int, db: Session) -> int:
        """Resolve organization ID for the user."""
        if user_role == 0:
            return 0
        membership = (
            db.query(OrganizationUser)
            .filter(OrganizationUser.user_id == user_id)
            .order_by(OrganizationUser.org_id)
            .first()
        )
        if not membership:
            raise TeacherGroupPermissionError("User does not belong to an organization")
        return membership.org_id

    @staticmethod
    def _build_response(group: TeacherGroup, db: Session) -> TeacherGroupResponse:
        """Helper to build a TeacherGroupResponse including teacher list."""
        active_gts = (
            db.query(GroupTeacher)
            .options(joinedload(GroupTeacher.teacher))
            .filter(
                GroupTeacher.group_id == group.id,
                GroupTeacher.is_deleted.is_(False),
            )
            .all()
        )

        teachers = [
            TeacherUserSummary.model_validate(gt.teacher)
            for gt in active_gts
            if gt.teacher is not None
        ]

        creator = (
            TeacherUserSummary.model_validate(group.creator)
            if group.creator
            else None
        )
        supervisor_user = (
            TeacherUserSummary.model_validate(group.supervisor_user)
            if group.supervisor_user
            else None
        )

        return TeacherGroupResponse(
            id=group.id,
            org_id=group.org_id,
            created_by=group.created_by,
            name=group.name,
            supervisor=group.supervisor,
            is_active=group.is_active,
            is_deleted=group.is_deleted,
            created_at=group.created_at,
            updated_at=group.updated_at,
            deleted_at=group.deleted_at,
            creator=creator,
            supervisor_user=supervisor_user,
            teachers=teachers,
        )

    @classmethod
    def create_group(
        cls,
        data: TeacherGroupCreate,
        user_id: int,
        user_role: int,
        db: Session,
    ) -> TeacherGroupResponse:
        """Create a new teacher group with assigned supervisor and teachers."""
        if user_role not in (0, 1, 2):
            raise TeacherGroupPermissionError("Only admins and teachers can create teacher groups")

        if user_role == 0:
            org_id = data.org_id if data.org_id is not None else 0
        else:
            org_id = cls._get_user_org_id(user_id, user_role, db)

        # Validate supervisor user exists
        supervisor_user = db.query(User).filter(User.id == data.supervisor).first()
        if not supervisor_user:
            raise TeacherGroupValidationError(f"Supervisor with user ID {data.supervisor} does not exist")

        # Validate teacher_ids exist
        if data.teacher_ids:
            existing_teachers = (
                db.query(User.id).filter(User.id.in_(data.teacher_ids)).all()
            )
            existing_ids = {t.id for t in existing_teachers}
            missing_ids = set(data.teacher_ids) - existing_ids
            if missing_ids:
                raise TeacherGroupValidationError(
                    f"Teacher user IDs do not exist: {sorted(list(missing_ids))}"
                )

        group = TeacherGroup(
            org_id=org_id,
            created_by=user_id,
            name=data.name,
            supervisor=data.supervisor,
            is_active=data.is_active,
            is_deleted=False,
        )

        try:
            db.add(group)
            db.flush()  # populate group.id

            # Add teachers to group_teachers
            for tid in set(data.teacher_ids):
                gt = GroupTeacher(
                    group_id=group.id,
                    teacher_id=tid,
                    is_deleted=False,
                )
                db.add(gt)

            db.commit()
            db.refresh(group)
        except Exception:
            db.rollback()
            raise

        return cls._build_response(group, db)

    @classmethod
    def get_all_groups(
        cls,
        user_id: int,
        user_role: int,
        db: Session,
    ) -> list[TeacherGroupResponse]:
        """Get all active, non-deleted teacher groups visible to the authenticated user."""
        if user_role not in (0, 1, 2, 3):
            return []

        query = (
            db.query(TeacherGroup)
            .options(
                joinedload(TeacherGroup.creator),
                joinedload(TeacherGroup.supervisor_user),
            )
            .filter(
                TeacherGroup.is_active.is_(True),
                TeacherGroup.is_deleted.is_(False),
            )
        )

        if user_role != 0:
            user_org_id = cls._get_user_org_id(user_id, user_role, db)
            query = query.filter(TeacherGroup.org_id == user_org_id)

        groups = query.order_by(TeacherGroup.id.desc()).all()
        return [cls._build_response(g, db) for g in groups]

    @classmethod
    def get_group_by_id(
        cls,
        group_id: int,
        user_id: int,
        user_role: int,
        db: Session,
    ) -> TeacherGroupResponse | None:
        """Fetch details for a single non-deleted teacher group."""
        group = (
            db.query(TeacherGroup)
            .options(
                joinedload(TeacherGroup.creator),
                joinedload(TeacherGroup.supervisor_user),
            )
            .filter(
                TeacherGroup.id == group_id,
                TeacherGroup.is_deleted.is_(False),
            )
            .first()
        )
        if not group:
            return None

        if user_role != 0:
            user_org_id = cls._get_user_org_id(user_id, user_role, db)
            if group.org_id != user_org_id:
                return None

        return cls._build_response(group, db)

    @classmethod
    def update_group(
        cls,
        group_id: int,
        data: TeacherGroupUpdate,
        user_id: int,
        user_role: int,
        db: Session,
    ) -> TeacherGroupResponse | None:
        """Update teacher group details and teacher assignments."""
        if user_role not in (0, 1, 2):
            raise TeacherGroupPermissionError("Only admins and teachers can update teacher groups")

        group = (
            db.query(TeacherGroup)
            .filter(
                TeacherGroup.id == group_id,
                TeacherGroup.is_deleted.is_(False),
            )
            .first()
        )
        if not group:
            return None

        if user_role != 0:
            user_org_id = cls._get_user_org_id(user_id, user_role, db)
            if group.org_id != user_org_id:
                raise TeacherGroupPermissionError(
                    "You can only update teacher groups belonging to your organization"
                )

        if data.supervisor is not None:
            supervisor_user = db.query(User).filter(User.id == data.supervisor).first()
            if not supervisor_user:
                raise TeacherGroupValidationError(
                    f"Supervisor with user ID {data.supervisor} does not exist"
                )
            group.supervisor = data.supervisor

        if data.name is not None:
            group.name = data.name

        if data.is_active is not None:
            group.is_active = data.is_active

        if data.teacher_ids is not None:
            target_ids = set(data.teacher_ids)
            if target_ids:
                existing_teachers = (
                    db.query(User.id).filter(User.id.in_(target_ids)).all()
                )
                existing_ids = {t.id for t in existing_teachers}
                missing_ids = target_ids - existing_ids
                if missing_ids:
                    raise TeacherGroupValidationError(
                        f"Teacher user IDs do not exist: {sorted(list(missing_ids))}"
                    )

            current_gts = (
                db.query(GroupTeacher)
                .filter(GroupTeacher.group_id == group_id)
                .all()
            )
            current_gt_map = {gt.teacher_id: gt for gt in current_gts}

            # Soft delete records no longer in teacher_ids
            for tid, gt in current_gt_map.items():
                if tid not in target_ids and not gt.is_deleted:
                    gt.is_deleted = True
                    gt.deleted_at = datetime.now(timezone.utc)

            # Add or re-enable records in target_ids
            for tid in target_ids:
                if tid in current_gt_map:
                    gt = current_gt_map[tid]
                    if gt.is_deleted:
                        gt.is_deleted = False
                        gt.deleted_at = None
                else:
                    new_gt = GroupTeacher(
                        group_id=group_id,
                        teacher_id=tid,
                        is_deleted=False,
                    )
                    db.add(new_gt)

        try:
            db.commit()
            db.refresh(group)
        except Exception:
            db.rollback()
            raise

        return cls._build_response(group, db)

    @classmethod
    def delete_group(
        cls,
        group_id: int,
        user_id: int,
        user_role: int,
        db: Session,
    ) -> bool:
        """Soft delete a teacher group and its group teachers."""
        if user_role not in (0, 1, 2):
            raise TeacherGroupPermissionError("Only admins and teachers can delete teacher groups")

        group = (
            db.query(TeacherGroup)
            .filter(
                TeacherGroup.id == group_id,
                TeacherGroup.is_deleted.is_(False),
            )
            .first()
        )
        if not group:
            return False

        if user_role != 0:
            user_org_id = cls._get_user_org_id(user_id, user_role, db)
            if group.org_id != user_org_id:
                raise TeacherGroupPermissionError(
                    "You can only delete teacher groups belonging to your organization"
                )

        now = datetime.now(timezone.utc)

        group.is_deleted = True
        group.is_active = False
        group.deleted_at = now

        # Soft delete associated group_teachers
        active_gts = (
            db.query(GroupTeacher)
            .filter(
                GroupTeacher.group_id == group_id,
                GroupTeacher.is_deleted.is_(False),
            )
            .all()
        )
        for gt in active_gts:
            gt.is_deleted = True
            gt.deleted_at = now

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        return True
