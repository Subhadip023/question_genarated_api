"""
Question routes — thin route definitions that delegate to the controller.
This acts as the View/Route (V) layer in MVC.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.controllers.question_controller import (
    QuestionController,
    QuestionCreatorHasNoOrganizationError,
)
from app.dependencies.db import get_db
from app.schemas.question import (
    BulkQuestionCreate,
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
)

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.post(
    "/",
    response_model=QuestionResponse,
    status_code=201,
    summary="Create a question",
    description="Store a new question (HTML content) in the database.",
)
def create_question(
    data: QuestionCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> QuestionResponse:
    try:
        return QuestionController.create_question(
            data,
            user_id=request.state.user_id,
            user_role=request.state.user_role,
            db=db,
        )
    except QuestionCreatorHasNoOrganizationError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc) or "User does not belong to an organization",
        )


@router.post(
    "/bulk",
    response_model=list[QuestionResponse],
    status_code=201,
    summary="Create multiple questions",
    description="Create multiple questions and their answer options atomically.",
)
def create_questions_bulk(
    data: list[BulkQuestionCreate],
    request: Request,
    db: Session = Depends(get_db),
) -> list[QuestionResponse]:
    if not data:
        raise HTTPException(status_code=422, detail="At least one question is required")
    try:
        return QuestionController.create_questions_bulk(
            data,
            user_id=request.state.user_id,
            user_role=request.state.user_role,
            db=db,
        )
    except QuestionCreatorHasNoOrganizationError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc) or "User does not belong to an organization",
        )


@router.get(
    "/",
    response_model=list[QuestionResponse],
    summary="List all questions",
)
def list_questions(
    request: Request,
    db: Session = Depends(get_db),
) -> list[QuestionResponse]:
    return QuestionController.get_all_questions(
        user_id=request.state.user_id,
        user_role=request.state.user_role,
        db=db,
    )


@router.get(
    "/{question_id}",
    response_model=QuestionResponse,
    summary="Get a question by ID",
)
def get_question(
    question_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> QuestionResponse:
    result = QuestionController.get_question(
        question_id,
        user_id=request.state.user_id,
        user_role=request.state.user_role,
        db=db,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return result


@router.patch(
    "/{question_id}",
    response_model=QuestionResponse,
    summary="Edit a question",
    description="Partially update a question. If options are supplied, they replace all existing options.",
)
def update_question(
    question_id: int,
    data: QuestionUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> QuestionResponse:
    if request.state.user_role not in (0, 1, 2):
        raise HTTPException(status_code=403, detail="Students cannot update questions")
    visible = QuestionController.get_question(
        question_id, request.state.user_id, request.state.user_role, db
    )
    if visible is None:
        raise HTTPException(status_code=404, detail="Question not found")
    result = QuestionController.update_question(question_id, data, db)
    if result is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return result


@router.delete(
    "/{question_id}",
    summary="Delete a question",
    description="Delete a question and all of its options.",
)
def delete_question(
    question_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    if request.state.user_role not in (0, 1, 2):
        raise HTTPException(status_code=403, detail="Students cannot delete questions")
    visible = QuestionController.get_question(
        question_id, request.state.user_id, request.state.user_role, db
    )
    if visible is None:
        raise HTTPException(status_code=404, detail="Question not found")
    deleted = QuestionController.delete_question(question_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"detail": "Question deleted"}
