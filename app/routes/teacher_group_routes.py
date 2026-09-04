"""FastAPI route handlers for teacher groups."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.controllers.teacher_group_controller import (
    TeacherGroupController,
    TeacherGroupPermissionError,
    TeacherGroupValidationError,
)
from app.dependencies.db import get_db
from app.schemas.teacher_group import (
    TeacherGroupCreate,
    TeacherGroupResponse,
    TeacherGroupUpdate,
)

router = APIRouter(prefix="/teacher-groups", tags=["Teacher Groups"])


@router.get(
    "",
    response_model=list[TeacherGroupResponse],
    summary="Get all teacher groups",
    description="Get all active teacher groups (is_active=1) visible to the authenticated user.",
)
@router.get(
    "/",
    response_model=list[TeacherGroupResponse],
    include_in_schema=False,
)
def list_teacher_groups(
    request: Request,
    db: Session = Depends(get_db),
) -> list[TeacherGroupResponse]:
    try:
        return TeacherGroupController.get_all_groups(
            user_id=request.state.user_id,
            user_role=request.state.user_role,
            db=db,
        )
    except TeacherGroupPermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.get(
    "/{group_id}",
    response_model=TeacherGroupResponse,
    summary="Get group details by ID",
)
def get_teacher_group(
    group_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> TeacherGroupResponse:
    group = TeacherGroupController.get_group_by_id(
        group_id=group_id,
        user_id=request.state.user_id,
        user_role=request.state.user_role,
        db=db,
    )
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher group not found or access denied",
        )
    return group


@router.post(
    "",
    response_model=TeacherGroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a teacher group",
)
@router.post(
    "/",
    response_model=TeacherGroupResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_teacher_group(
    data: TeacherGroupCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> TeacherGroupResponse:
    try:
        return TeacherGroupController.create_group(
            data=data,
            user_id=request.state.user_id,
            user_role=request.state.user_role,
            db=db,
        )
    except TeacherGroupPermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except TeacherGroupValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.put(
    "/{group_id}",
    response_model=TeacherGroupResponse,
    summary="Edit a teacher group",
)
def update_teacher_group(
    group_id: int,
    data: TeacherGroupUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> TeacherGroupResponse:
    try:
        group = TeacherGroupController.update_group(
            group_id=group_id,
            data=data,
            user_id=request.state.user_id,
            user_role=request.state.user_role,
            db=db,
        )
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher group not found",
            )
        return group
    except TeacherGroupPermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except TeacherGroupValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete(
    "/{group_id}",
    summary="Soft delete a teacher group",
)
def delete_teacher_group(
    group_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        deleted = TeacherGroupController.delete_group(
            group_id=group_id,
            user_id=request.state.user_id,
            user_role=request.state.user_role,
            db=db,
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher group not found",
            )
        return {"detail": "Teacher group soft deleted successfully"}
    except TeacherGroupPermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
