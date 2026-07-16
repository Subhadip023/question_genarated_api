"""HTTP routes for user CRUD operations."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.controllers.user_controller import UserController, UserEmailExistsError
from app.dependencies.db import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    try:
        return UserController.create_user(data, db)
    except UserEmailExistsError:
        raise HTTPException(status_code=409, detail="Email already exists") from None


@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)) -> list[UserResponse]:
    return UserController.get_all_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    user = UserController.get_user(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, data: UserUpdate, db: Session = Depends(get_db)
) -> UserResponse:
    try:
        user = UserController.update_user(user_id, data, db)
    except UserEmailExistsError:
        raise HTTPException(status_code=409, detail="Email already exists") from None
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> Response:
    if not UserController.delete_user(user_id, db):
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
