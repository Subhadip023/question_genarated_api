from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.diagram import Diagram
from app.models.organization import Organization
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.schemas.diagram import DiagramCreate
from app.services.file_service import FileService


from app.models.organization_user import OrganizationUser


class DiagramTypeValidationError(Exception):
    pass


class DiagramReferenceNotFoundError(Exception):
    pass


class DiagramOrganizationNotFoundError(Exception):
    pass


class DiagramNotFoundError(Exception):
    pass


class DiagramController:
    """Controller responsible for diagram creation, retrieval, update, and deletion."""

    @staticmethod
    def _resolve_org_id(org_id: int, diagram_type: int, ref_id: int, user_id: int, db: Session) -> int:
        """Resolve organization ID for diagram record."""
        if org_id != 0:
            return org_id

        # 1. Try to get org_id from referred Question
        if diagram_type == 0:
            q_org = db.scalar(select(Question.organization_id).where(Question.id == ref_id))
            if q_org is not None:
                return q_org
        else:
            opt_q_id = db.scalar(select(QuestionOption.q_id).where(QuestionOption.id == ref_id))
            if opt_q_id:
                q_org = db.scalar(select(Question.organization_id).where(Question.id == opt_q_id))
                if q_org is not None:
                    return q_org

        # 2. Try to get org_id from user's membership
        user_org = db.scalar(select(OrganizationUser.org_id).where(OrganizationUser.user_id == user_id))
        if user_org is not None:
            return user_org

        return 0

    @staticmethod
    def upload_and_create_diagram(
        file: UploadFile,
        diagram_type: int,
        ref_id: int,
        org_id: int,
        user_id: int,
        db: Session,
    ) -> Diagram:
        """Upload a file, save it to disk, and record the diagram entry in DB."""
        if diagram_type not in (0, 1):
            raise DiagramTypeValidationError("type must be 0 or 1 (0 for Question, 1 for Option)")

        if diagram_type == 0:
            if not db.scalar(select(Question.id).where(Question.id == ref_id)):
                raise DiagramReferenceNotFoundError("Question not found for ref_id")
        else:
            if not db.scalar(select(QuestionOption.id).where(QuestionOption.id == ref_id)):
                raise DiagramReferenceNotFoundError("Question option not found for ref_id")

        resolved_org_id = DiagramController._resolve_org_id(org_id, diagram_type, ref_id, user_id, db)
        saved_path = FileService.save_diagram_file(file=file, diagram_type=diagram_type)

        diagram = Diagram(
            type=diagram_type,
            ref_id=ref_id,
            org_id=resolved_org_id,
            user_id=user_id,
            path=saved_path,
        )

        try:
            db.add(diagram)
            db.commit()
            db.refresh(diagram)
        except Exception:
            db.rollback()
            FileService.delete_file(saved_path)
            raise

        return diagram

    @staticmethod
    def create_diagram(data: DiagramCreate, user_id: int, db: Session) -> Diagram:
        if data.type not in (0, 1):
            raise DiagramTypeValidationError("type must be 0 or 1")

        if data.type == 0:
            if not db.scalar(select(Question.id).where(Question.id == data.ref_id)):
                raise DiagramReferenceNotFoundError("Question not found for ref_id")
        else:
            if not db.scalar(select(QuestionOption.id).where(QuestionOption.id == data.ref_id)):
                raise DiagramReferenceNotFoundError("Question option not found for ref_id")

        resolved_org_id = DiagramController._resolve_org_id(data.org_id, data.type, data.ref_id, user_id, db)

        diagram = Diagram(
            type=data.type,
            ref_id=data.ref_id,
            org_id=resolved_org_id,
            user_id=user_id,
            path=data.path,
        )

        try:
            db.add(diagram)
            db.commit()
            db.refresh(diagram)
        except Exception:
            db.rollback()
            raise

        return diagram

    @staticmethod
    def list_diagrams(db: Session) -> list[Diagram]:
        return db.query(Diagram).order_by(Diagram.id.desc()).all()

    @staticmethod
    def get_diagram(diagram_id: int, db: Session) -> Diagram:
        """Fetch single diagram by ID."""
        diagram = db.query(Diagram).filter(Diagram.id == diagram_id).first()
        if not diagram:
            raise DiagramNotFoundError(f"Diagram with ID {diagram_id} not found")
        return diagram

    @staticmethod
    def update_diagram_file(
        diagram_id: int,
        file: UploadFile,
        user_id: int,
        db: Session,
    ) -> Diagram:
        """Replace an existing diagram file with a new file and update path in DB."""
        diagram = DiagramController.get_diagram(diagram_id, db)
        old_path = diagram.path

        new_path = FileService.save_diagram_file(file=file, diagram_type=diagram.type)
        diagram.path = new_path
        if user_id:
            diagram.user_id = user_id

        try:
            db.commit()
            db.refresh(diagram)
            # Remove old file after successful DB commit
            if old_path and old_path != new_path:
                FileService.delete_file(old_path)
        except Exception:
            db.rollback()
            FileService.delete_file(new_path)
            raise

        return diagram

    @staticmethod
    def delete_diagram(diagram_id: int, db: Session) -> bool:
        """Delete diagram database record and remove local image file from disk."""
        diagram = db.query(Diagram).filter(Diagram.id == diagram_id).first()
        if not diagram:
            raise DiagramNotFoundError(f"Diagram with ID {diagram_id} not found")

        path = diagram.path
        try:
            db.delete(diagram)
            db.commit()
            if path:
                FileService.delete_file(path)
        except Exception:
            db.rollback()
            raise

        return True
