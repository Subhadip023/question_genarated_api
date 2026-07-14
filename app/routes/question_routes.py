"""
Question routes — thin route definitions that delegate to the controller.
This acts as the View/Route (V) layer in MVC.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.controllers.question_controller import QuestionController
from app.dependencies.db import get_db
from app.schemas.question import QuestionCreate, QuestionResponse

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
    db: Session = Depends(get_db),
) -> QuestionResponse:
    return QuestionController.create_question(data, db)


@router.get(
    "/",
    response_model=list[QuestionResponse],
    summary="List all questions",
)
def list_questions(db: Session = Depends(get_db)) -> list[QuestionResponse]:
    return QuestionController.get_all_questions(db)


@router.get(
    "/{question_id}",
    response_model=QuestionResponse,
    summary="Get a question by ID",
)
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
) -> QuestionResponse:
    result = QuestionController.get_question(question_id, db)
    if result is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return result
