"""Authentication controller."""

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import create_access_token, verify_password


class InvalidCredentialsError(Exception):
    """Raised when login credentials are incorrect."""


class AuthController:
    @staticmethod
    def login(data: LoginRequest, db: Session) -> TokenResponse:
        user = (
            db.query(User)
            .filter(User.email == data.email.strip().lower())
            .first()
        )
        if user is None or not verify_password(data.password, user.password):
            raise InvalidCredentialsError

        token, expires_in = create_access_token(user.id, user.role)
        return TokenResponse(
            message=f"Welcome, {user.name}!",
            access_token=token,
            expires_in=expires_in,
            user=UserResponse.model_validate(user),
        )
