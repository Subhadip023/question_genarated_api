"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.controllers.auth_controller import (
    AuthController,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidOldPasswordError,
    PasswordConfirmationError,
)
from app.dependencies.db import get_db
from app.schemas.user import (
    LoginRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    StudentRegister,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register_student(
    data: StudentRegister, db: Session = Depends(get_db)
) -> UserResponse:
    try:
        return AuthController.register_student(data, db)
    except EmailAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Email already exists") from None


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        return AuthController.login(data, db)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


@router.post("/reset-password", response_model=ResetPasswordResponse)
def reset_password(
    data: ResetPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ResetPasswordResponse:
    try:
        return AuthController.reset_password(request.state.user_id, data, db)
    except InvalidOldPasswordError:
        raise HTTPException(status_code=400, detail="Old password is incorrect") from None
    except PasswordConfirmationError:
        raise HTTPException(
            status_code=400,
            detail="New password and confirmation do not match",
        ) from None
