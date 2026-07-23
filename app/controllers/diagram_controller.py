from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.diagram import Diagram
from app.models.organization import Organization
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.schemas.diagram import DiagramCreate


class DiagramTypeValidationError(Exception):
    pass


class DiagramReferenceNotFoundError(Exception):
    pass


class DiagramOrganizationNotFoundError(Exception):
    pass


class DiagramController:
    """Controller responsible for diagram creation and validation."""

    @staticmethod
    def create_diagram(data: DiagramCreate, user_id: int, db: Session) -> Diagram:
        if data.type not in (0, 1):
            raise DiagramTypeValidationError("type must be 0 or 1")

        if not db.scalar(select(Organization.id).where(Organization.id == data.org_id)):
            raise DiagramOrganizationNotFoundError("Organization not found")

        if data.type == 0:
            if not db.scalar(select(Question.id).where(Question.id == data.ref_id)):
                raise DiagramReferenceNotFoundError("Question not found for ref_id")
        else:
            if not db.scalar(select(QuestionOption.id).where(QuestionOption.id == data.ref_id)):
                raise DiagramReferenceNotFoundError("Question option not found for ref_id")

        diagram = Diagram(
            type=data.type,
            ref_id=data.ref_id,
            org_id=data.org_id,
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
