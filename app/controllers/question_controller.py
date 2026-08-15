"""
Question controller — handles request orchestration between route and model.
This acts as the Controller (C) layer in MVC.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.diagram import Diagram
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.organization_user import OrganizationUser
from app.schemas.diagram import DiagramResponse
from app.schemas.question import (
    BulkQuestionCreate,
    PaginatedQuestionResponse,
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
)


class QuestionCreatorHasNoOrganizationError(Exception):
    """Raised when a non-superadmin has no organization membership."""


class QuestionController:
    """Controller responsible for handling question-related business logic."""

    @staticmethod
    def get_health() -> dict:
        """Return API health status."""
        return {"status": 1,"message": "Healthy"}

    @staticmethod
    def get_welcome() -> dict:
        """Return welcome message."""
        return {"message": "Welcome to QMaster!"}

    @staticmethod
    def create_question(
        data: QuestionCreate,
        user_id: int,
        user_role: int,
        db: Session,
    ) -> QuestionResponse:
        """Insert a question and its options in one transaction."""
        if user_role not in (0, 1, 2):
            raise QuestionCreatorHasNoOrganizationError(
                "Only roles 0, 1, and 2 can create questions"
            )
        if user_role == 0:
            organization_id = 0
            is_global = True
        else:
            membership = (
                db.query(OrganizationUser)
                .filter(OrganizationUser.user_id == user_id)
                .order_by(OrganizationUser.org_id)
                .first()
            )
            if membership is None:
                raise QuestionCreatorHasNoOrganizationError
            organization_id = membership.org_id
            is_global = False

        question = Question(
            question=data.question,
            organization_id=organization_id,
            user_id=user_id,
            is_global=is_global,
            marks=data.marks,
            is_active=data.is_active,
            topic_id=data.topic_id,
            options=[
                QuestionOption(
                    ans=option.ans,
                    is_correct=option.is_correct,
                )
                for option in data.options
            ],
        )

        try:
            db.add(question)
            db.commit()
        except Exception:
            db.rollback()
            raise

        question = (
            db.query(Question)
            .options(joinedload(Question.options), joinedload(Question.topic))
            .filter(Question.id == question.id)
            .first()
        )
        return QuestionController._build_question_response(question, db)

    @staticmethod
    def _build_question_response(question: Question, db: Session) -> QuestionResponse:
        """Attach diagrams list, diagram_id, and diagram_path to QuestionResponse, and populate option diagrams."""
        response = QuestionResponse.model_validate(question)
        diagrams = (
            db.query(Diagram)
            .filter(Diagram.type == 0, Diagram.ref_id == question.id)
            .order_by(Diagram.id.asc())
            .all()
        )
        if diagrams:
            response.diagrams = [DiagramResponse.model_validate(d) for d in diagrams]
            latest = diagrams[-1]
            response.diagram_id = latest.id
            response.diagram_path = latest.path

        # Option diagrams (type = 1)
        option_ids = [opt.id for opt in question.options if opt.id]
        if option_ids:
            opt_diagrams = (
                db.query(Diagram)
                .filter(Diagram.type == 1, Diagram.ref_id.in_(option_ids))
                .order_by(Diagram.id.desc())
                .all()
            )
            opt_diag_map = {}
            for d in opt_diagrams:
                if d.ref_id not in opt_diag_map:
                    opt_diag_map[d.ref_id] = d
            for opt_res in response.options:
                if opt_res.id in opt_diag_map:
                    d = opt_diag_map[opt_res.id]
                    opt_res.diagram_id = d.id
                    opt_res.diagram_path = d.path

        return response

    @staticmethod
    def create_questions_bulk(
        items: list[BulkQuestionCreate],
        user_id: int,
        user_role: int,
        db: Session,
    ) -> list[QuestionResponse]:
        """Insert multiple questions and their options in one transaction."""
        organization_id, is_global = QuestionController._creator_scope(
            user_id, user_role, db
        )
        questions = [
            Question(
                question=item.question,
                organization_id=organization_id,
                user_id=user_id,
                is_global=is_global,
                marks=item.marks,
                is_active=item.is_active,
                topic_id=item.topic_id,
                options=[
                    QuestionOption(ans=option.ans, is_correct=option.is_correct)
                    for option in item.options
                ],
            )
            for item in items
        ]

        try:
            db.add_all(questions)
            db.flush()
            question_ids = [question.id for question in questions]
            db.commit()
        except Exception:
            db.rollback()
            raise

        created = (
            db.query(Question)
            .options(joinedload(Question.options), joinedload(Question.topic))
            .filter(Question.id.in_(question_ids))
            .all()
        )
        created_by_id = {question.id: question for question in created}
        return [
            QuestionController._build_question_response(created_by_id[question_id], db)
            for question_id in question_ids
        ]

    @staticmethod
    def _creator_scope(
        user_id: int, user_role: int, db: Session
    ) -> tuple[int, bool]:
        """Resolve ownership fields for a bulk-question creator."""
        if user_role not in (0,1,2):
            raise QuestionCreatorHasNoOrganizationError(
                "Only roles 1 and 2 can create questions in bulk"
            )

        membership = (
            db.query(OrganizationUser)
            .filter(OrganizationUser.user_id == user_id)
            .order_by(OrganizationUser.org_id)
            .first()
        )
        if membership is None:
            raise QuestionCreatorHasNoOrganizationError(
                "User does not belong to an organization"
            )
        return membership.org_id, False

    @staticmethod
    def get_all_questions(
        user_id: int,
        user_role: int,
        page: int,
        page_size: int,
        db: Session,
        topic_id: int | None = None,
        search: str | None = None,
    ) -> PaginatedQuestionResponse:
        """Fetch one page of questions visible to the authenticated user."""
        query = db.query(Question)
        query = QuestionController._apply_visibility_filter(
            query, user_id, user_role, db
        )
        if topic_id is not None:
            query = query.filter(Question.topic_id == topic_id)
        if search:
            query = query.filter(Question.question.ilike(f"%{search}%"))
        total = query.count()
        questions = (
            query.options(joinedload(Question.options), joinedload(Question.topic))
            .order_by(Question.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        question_ids = [q.id for q in questions]
        diagrams_map: dict[int, list[DiagramResponse]] = {}
        if question_ids:
            diagrams = (
                db.query(Diagram)
                .filter(Diagram.type == 0, Diagram.ref_id.in_(question_ids))
                .order_by(Diagram.id.asc())
                .all()
            )
            for d in diagrams:
                if d.ref_id not in diagrams_map:
                    diagrams_map[d.ref_id] = []
                diagrams_map[d.ref_id].append(DiagramResponse.model_validate(d))

        all_option_ids = [opt.id for q in questions for opt in q.options if opt.id]
        opt_diag_map = {}
        if all_option_ids:
            opt_diagrams = (
                db.query(Diagram)
                .filter(Diagram.type == 1, Diagram.ref_id.in_(all_option_ids))
                .order_by(Diagram.id.desc())
                .all()
            )
            for d in opt_diagrams:
                if d.ref_id not in opt_diag_map:
                    opt_diag_map[d.ref_id] = d

        items = []
        for q in questions:
            res = QuestionResponse.model_validate(q)
            if q.id in diagrams_map:
                res.diagrams = diagrams_map[q.id]
                latest = diagrams_map[q.id][-1]
                res.diagram_id = latest.id
                res.diagram_path = latest.path
            for opt_res in res.options:
                if opt_res.id in opt_diag_map:
                    d = opt_diag_map[opt_res.id]
                    opt_res.diagram_id = d.id
                    opt_res.diagram_path = d.path
            items.append(res)

        return PaginatedQuestionResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )

    @staticmethod
    def get_question(
        question_id: int,
        user_id: int,
        user_role: int,
        db: Session,
    ) -> QuestionResponse | None:
        """Fetch a question only when it is visible to the authenticated user."""
        query = (
            db.query(Question)
            .options(joinedload(Question.options), joinedload(Question.topic))
            .filter(Question.id == question_id)
        )
        query = QuestionController._apply_visibility_filter(
            query, user_id, user_role, db
        )
        question = query.first()
        if not question:
            return None
        return QuestionController._build_question_response(question, db)

    @staticmethod
    def _apply_visibility_filter(query, user_id: int, user_role: int, db: Session):
        """Apply role-based question visibility to a SQLAlchemy query."""
        if user_role == 0:
            return query

        if user_role == 1:
            organization_ids = (
                select(OrganizationUser.org_id)
                .filter(OrganizationUser.user_id == user_id)
            )
            return query.filter(Question.organization_id.in_(organization_ids))

        if user_role == 2:
            return query.filter(Question.user_id == user_id)

        return query.filter(False)

    @staticmethod
    def update_question(
        question_id: int,
        data: QuestionUpdate,
        db: Session,
    ) -> QuestionResponse | None:
        """Partially update a question and optionally replace all its options."""
        question = (
            db.query(Question)
            .options(joinedload(Question.options), joinedload(Question.topic))
            .filter(Question.id == question_id)
            .first()
        )
        if question is None:
            return None

        updates = data.model_dump(exclude_unset=True)
        options = updates.pop("options", None)

        for field, value in updates.items():
            if value is not None:
                setattr(question, field, value)

        if options is not None:
            question.options = [QuestionOption(**option) for option in options]

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        question = (
            db.query(Question)
            .options(joinedload(Question.options), joinedload(Question.topic))
            .filter(Question.id == question_id)
            .first()
        )
        return QuestionController._build_question_response(question, db)

    @staticmethod
    def delete_question(question_id: int, db: Session) -> bool:
        """Delete a question and its related options."""
        question = (
            db.query(Question)
            .filter(Question.id == question_id)
            .first()
        )
        if question is None:
            return False

        try:
            db.delete(question)
            db.commit()
        except Exception:
            db.rollback()
            raise

        return True
