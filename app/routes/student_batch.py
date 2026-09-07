from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_org_id

from app.controllers.student_batch_controller import (
    StudentBatchController,
)

from app.schemas.student_batch import (
    AddBatchStudentsRequest,
    BatchStudentUserResponse,
    StudentBatchCreate,
    StudentBatchResponse,
    StudentBatchUpdate,
)

router = APIRouter(
    prefix="/student-batches",
    tags=["Student Batches"],
)

@router.post(
    "",
    response_model=StudentBatchResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_student_batch(
    payload: StudentBatchCreate,
    org_id: int = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    return StudentBatchController.create_batch(
        db=db,
        org_id=org_id,
        payload=payload,
    )

@router.get(
    "",
    response_model=list[StudentBatchResponse],
)
def get_all_student_batches(
    org_id: int = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    return StudentBatchController.get_all_batches(
        db=db,
        org_id=org_id,
    )

@router.get(
    "/{batch_id}",
    response_model=StudentBatchResponse,
)
def get_student_batch(
    batch_id: int,
    org_id: int = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    return StudentBatchController.get_batch(
        db=db,
        org_id=org_id,
        batch_id=batch_id,
    )

@router.put(
    "/{batch_id}",
    response_model=StudentBatchResponse,
)
def update_student_batch(
    batch_id: int,
    payload: StudentBatchUpdate,
    org_id: int = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    return StudentBatchController.update_batch(
        db=db,
        org_id=org_id,
        batch_id=batch_id,
        payload=payload,
    )

@router.delete("/{batch_id}")
def delete_student_batch(
    batch_id: int,
    org_id: int = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    return StudentBatchController.delete_batch(
        db=db,
        org_id=org_id,
        batch_id=batch_id,
    )

@router.get(
    "/{batch_id}/students",
    response_model=list[BatchStudentUserResponse],
)
def get_batch_students(
    batch_id: int,
    org_id: int = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    return StudentBatchController.get_batch_students(
        db=db,
        org_id=org_id,
        batch_id=batch_id,
    )

@router.post("/{batch_id}/students")
def add_batch_students(
    batch_id: int,
    payload: AddBatchStudentsRequest,
    org_id: int = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    return StudentBatchController.add_batch_students(
        db=db,
        org_id=org_id,
        batch_id=batch_id,
        payload=payload,
    )

@router.delete(
    "/{batch_id}/students/{student_id}"
)
def remove_batch_student(
    batch_id: int,
    student_id: int,
    org_id: int = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    return StudentBatchController.remove_batch_student(
        db=db,
        org_id=org_id,
        batch_id=batch_id,
        student_id=student_id,
    )