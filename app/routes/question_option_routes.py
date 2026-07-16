"""
QuestionOption routes — nested under /questions/{q_id}/options.
View (V) layer in MVC.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.controllers.question_option_controller import QuestionOptionController
from app.controllers.question_controller import QuestionController
from app.dependencies.db import get_db
from app.schemas.question_option import OptionCreate, OptionResponse

router = APIRouter(prefix="/questions/{q_id}/options", tags=["Options"])


def _require_question_access(q_id: int, request: Request, db: Session) -> None:
    if request.state.user_role not in (0, 1, 2):
        raise HTTPException(
            status_code=403,
            detail="Correct answers are restricted to roles 0, 1, and 2",
        )
    question = QuestionController.get_question(
        q_id, request.state.user_id, request.state.user_role, db
    )
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")


@router.post(
    "/",
    response_model=OptionResponse,
    status_code=201,
    summary="Add an option to a question",
)
def add_option(
    q_id: int,
    data: OptionCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> OptionResponse:
    _require_question_access(q_id, request, db)
    return QuestionOptionController.add_option(q_id, data, db)


@router.get(
    "/",
    response_model=list[OptionResponse],
    summary="Get all options for a question",
)
def get_options(
    q_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> list[OptionResponse]:
    _require_question_access(q_id, request, db)
    return QuestionOptionController.get_options(q_id, db)


@router.delete(
    "/{option_id}",
    summary="Delete an option",
)
def delete_option(
    q_id: int,
    option_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    _require_question_access(q_id, request, db)
    return QuestionOptionController.delete_option(q_id, option_id, db)
