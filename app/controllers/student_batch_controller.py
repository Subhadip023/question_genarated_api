from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization_user import OrganizationUser
from app.models.batch import Batch
from app.models.batch_student import BatchStudent
from app.models.user import User

from app.schemas.student_batch import (
    AddBatchStudentsRequest,
    StudentBatchCreate,
    StudentBatchUpdate,
)


class StudentBatchController:

    @staticmethod
    def get_all_batches(
        db: Session,
        org_id: int,
    ):
        batches = (
            db.query(Batch)
            .filter(
                Batch.org_id == org_id,
                Batch.is_active == True,
                Batch.deleted_at.is_(None),
            )
            .order_by(Batch.id.desc())
            .all()
        )

        return batches

    @staticmethod
    def get_batch(
        db: Session,
        org_id: int,
        batch_id: int,
    ):
        batch = (
            db.query(Batch)
            .filter(
                Batch.id == batch_id,
                Batch.org_id == org_id,
                Batch.deleted_at.is_(None),
            )
            .first()
        )

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student batch not found",
            )

        return batch

    @staticmethod
    def create_batch(
        db: Session,
        org_id: int,
        payload: StudentBatchCreate,
    ):
        supervisor = (
            db.query(User)
            .join(
                OrganizationUser,
                OrganizationUser.user_id == User.id,
            )
            .filter(
                User.id == payload.supervisor,
                OrganizationUser.org_id == org_id,
            )
            .first()
        )

        if not supervisor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supervisor not found in this organization",
            )

        # Change these role values according to your project.
        # 1 = organization admin
        # 2 = organization teacher
        if supervisor.role not in [1, 2]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supervisor must be an organization admin or teacher",
            )

        batch = Batch(
            org_id=org_id,
            name=payload.name,
            supervisor=payload.supervisor,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(batch)
        db.commit()
        db.refresh(batch)

        return batch

    @staticmethod
    def update_batch(
        db: Session,
        org_id: int,
        batch_id: int,
        payload: StudentBatchUpdate,
    ):
        batch = StudentBatchController.get_batch(
            db=db,
            org_id=org_id,
            batch_id=batch_id,
        )

        if payload.name is not None:
            batch.name = payload.name

        if payload.supervisor is not None:
            supervisor = (
                db.query(User)
                .join(
                    OrganizationUser,
                    OrganizationUser.user_id == User.id,
                )
                .filter(
                    User.id == payload.supervisor,
                    OrganizationUser.org_id == org_id,
                )
                .first()
            )

            if not supervisor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Supervisor not found in this organization",
                )

            if supervisor.role not in [1, 2]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Supervisor must be an organization admin or teacher",
                )

            batch.supervisor = payload.supervisor

        if payload.is_active is not None:
            batch.is_active = payload.is_active

        batch.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(batch)

        return batch

    @staticmethod
    def delete_batch(
        db: Session,
        org_id: int,
        batch_id: int,
    ):
        batch = StudentBatchController.get_batch(
            db=db,
            org_id=org_id,
            batch_id=batch_id,
        )

        batch.is_active = False
        batch.deleted_at = datetime.utcnow()
        batch.updated_at = datetime.utcnow()

        db.commit()

        return {
            "message": "Student batch deleted successfully"
        }

    @staticmethod
    def get_batch_students(
        db: Session,
        org_id: int,
        batch_id: int,
    ):
        batch = StudentBatchController.get_batch(
            db=db,
            org_id=org_id,
            batch_id=batch_id,
        )

        students = (
            db.query(BatchStudent, User)
            .join(User, User.id == BatchStudent.student_id)
            .filter(BatchStudent.batch_id == batch.id)
            .order_by(BatchStudent.id.desc())
            .all()
        )

        result = []

        for batch_student, student in students:
            result.append(
                {
                    "id": batch_student.id,
                    "student_id": student.id,
                    "name": getattr(student, "name", None),
                    "email": getattr(student, "email", None),
                }
            )

        return result

    @staticmethod
    def add_batch_students(
        db: Session,
        org_id: int,
        batch_id: int,
        payload: AddBatchStudentsRequest,
    ):
        batch = StudentBatchController.get_batch(
            db=db,
            org_id=org_id,
            batch_id=batch_id,
        )

        # Remove duplicate IDs from request.
        student_ids = list(set(payload.student_ids))

        students = (
            db.query(User)
            .join(
                OrganizationUser,
                OrganizationUser.user_id == User.id,
            )
            .filter(
                User.id.in_(student_ids),
                OrganizationUser.org_id == org_id,
                User.role == 3,
            )
            .all()
        )

        valid_student_ids = {student.id for student in students}

        invalid_student_ids = [
            student_id
            for student_id in student_ids
            if student_id not in valid_student_ids
        ]

        if invalid_student_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Some students are invalid or do not belong to this organization",
                    "student_ids": invalid_student_ids,
                },
            )

        existing_assignments = (
            db.query(BatchStudent)
            .filter(
                BatchStudent.batch_id == batch.id,
                BatchStudent.student_id.in_(student_ids),
            )
            .all()
        )

        existing_student_ids = {
            assignment.student_id
            for assignment in existing_assignments
        }

        new_student_ids = [
            student_id
            for student_id in student_ids
            if student_id not in existing_student_ids
        ]

        for student_id in new_student_ids:
            assignment = BatchStudent(
                batch_id=batch.id,
                student_id=student_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            db.add(assignment)

        db.commit()

        return {
            "message": "Students added to batch successfully",
            "batch_id": batch.id,
            "added_student_ids": new_student_ids,
            "already_assigned_student_ids": list(existing_student_ids),
        }

    @staticmethod
    def remove_batch_student(
        db: Session,
        org_id: int,
        batch_id: int,
        student_id: int,
    ):
        batch = StudentBatchController.get_batch(
            db=db,
            org_id=org_id,
            batch_id=batch_id,
        )

        assignment = (
            db.query(BatchStudent)
            .filter(
                BatchStudent.batch_id == batch.id,
                BatchStudent.student_id == student_id,
            )
            .first()
        )

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student is not assigned to this batch",
            )

        db.delete(assignment)
        db.commit()

        return {
            "message": "Student removed from batch successfully"
        }