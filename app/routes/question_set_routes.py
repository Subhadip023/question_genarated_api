from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.question_set import QuestionSetCreate

from app.controllers.question_set_controller import create_question_set, get_question_sets, get_question_set

from app.dependencies.auth import get_current_user



router = APIRouter(
    prefix="/question-sets",
    tags=["Question Sets"]
)



@router.post("")
def create_set(
    data: QuestionSetCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    return create_question_set(
        db,
        data,
        current_user
    )

@router.get("")
def list_question_sets(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    return get_question_sets(
        db,
        current_user
    )

@router.get("/{id}")
def show_question_set(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_question_set(db, id, current_user)