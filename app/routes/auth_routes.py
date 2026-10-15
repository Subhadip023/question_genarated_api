"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.controllers.auth_controller import (
    AccountDeactivatedError,
    AuthController,
    EmailAlreadyExistsError,
    ExpiredOTPError,
    InvalidCredentialsError,
    InvalidOldPasswordError,
    InvalidOTPError,
    PasswordConfirmationError,
    PasswordTooShortError,
)
from app.dependencies.db import get_db
from app.schemas.user import (
    ForgotPasswordResetRequest,
    ForgotPasswordResponse,
    ForgotPasswordSendOtpRequest,
    LoginRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    StudentRegister,
    TokenResponse,
    UserResponse,
)
from app.services.mail_service import MailServiceError

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
    except AccountDeactivatedError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc) or "Account is not active, Contact to super admin",
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


@router.post("/forgot-password/send-otp", response_model=ForgotPasswordResponse)
def send_forgot_password_otp(
    data: ForgotPasswordSendOtpRequest,
    db: Session = Depends(get_db),
) -> ForgotPasswordResponse:
    try:
        return AuthController.send_forgot_password_otp(data.email, db)
    except MailServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from None
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to process password reset request") from None


@router.post("/forgot-password/reset", response_model=ForgotPasswordResponse)
def reset_password_with_otp(
    data: ForgotPasswordResetRequest,
    db: Session = Depends(get_db),
) -> ForgotPasswordResponse:
    try:
        return AuthController.reset_password_with_otp(data, db)
    except PasswordConfirmationError as exc:
        raise HTTPException(status_code=400, detail=str(exc) or "New password and confirmation do not match") from None
    except PasswordTooShortError as exc:
        raise HTTPException(status_code=400, detail=str(exc) or "Password must be at least 8 characters") from None
    except InvalidOTPError as exc:
        raise HTTPException(status_code=400, detail=str(exc) or "Invalid email or verification code") from None
    except ExpiredOTPError as exc:
        raise HTTPException(status_code=400, detail=str(exc) or "Verification code has expired. Please request a new one.") from None
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to reset password. Please try again.") from None

