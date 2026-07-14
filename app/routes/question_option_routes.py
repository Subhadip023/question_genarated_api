"""
QuestionOption routes — nested under /questions/{q_id}/options.
View (V) layer in MVC.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.question_option_controller import QuestionOptionController
from app.dependencies.db import get_db
from app.schemas.question_option import OptionCreate, OptionResponse

router = APIRouter(prefix="/questions/{q_id}/options", tags=["Options"])


@router.post(
    "/",
    response_model=OptionResponse,
    status_code=201,
    summary="Add an option to a question",
)
def add_option(
    q_id: int,
    data: OptionCreate,
    db: Session = Depends(get_db),
) -> OptionResponse:
    return QuestionOptionController.add_option(q_id, data, db)


@router.get(
    "/",
    response_model=list[OptionResponse],
    summary="Get all options for a question",
)
def get_options(
    q_id: int,
    db: Session = Depends(get_db),
) -> list[OptionResponse]:
    return QuestionOptionController.get_options(q_id, db)


@router.delete(
    "/{option_id}",
    summary="Delete an option",
)
def delete_option(
    q_id: int,
    option_id: int,
    db: Session = Depends(get_db),
) -> dict:
    return QuestionOptionController.delete_option(option_id, db)
