from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.question_set import QuestionSetCreate, QuestionSetUpdate, AddQuestionsRequest

from app.controllers.question_set_controller import create_question_set, get_question_sets, get_question_set, update_question_set, delete_question_set, add_questions_to_set, remove_question_from_set, copy_question_set, get_question_sets_by_org

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

@router.put("/{id}")
def update_set(
    id: int,
    data: QuestionSetUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return update_question_set(
        db,
        id,
        data,
        current_user
    )

@router.delete("/{id}")
def delete_set(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return delete_question_set(
        db,
        id,
        current_user
    )

@router.post("/{id}/questions")
def add_questions(
    id: int,
    data: AddQuestionsRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return add_questions_to_set(
        db,
        id,
        data,
        current_user
    )

@router.delete("/{id}/questions/{question_id}")
def remove_question(
    id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return remove_question_from_set(
        db,
        id,
        question_id,
        current_user
    )

@router.post("/{id}/copy")
def copy_set(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return copy_question_set(
        db,
        id,
        current_user
    )

@router.get("/organization/{org_id}")
def get_org_question_sets(
    org_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return get_question_sets_by_org(
        db,
        org_id,
        current_user
    )