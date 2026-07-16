"""Authentication controller."""

from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.organization_user import OrganizationUser
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

        if user.role == 0:
            organization_id = 0
            organization_name = "Global"
        else:
            organization = (
                db.query(Organization)
                .join(OrganizationUser, OrganizationUser.org_id == Organization.id)
                .filter(OrganizationUser.user_id == user.id)
                .order_by(Organization.id)
                .first()
            )
            organization_id = organization.id if organization else None
            organization_name = organization.name if organization else None

        token, expires_in = create_access_token(user.id, user.role)
        return TokenResponse(
            message=f"Welcome, {user.name}!",
            access_token=token,
            expires_in=expires_in,
            organization_id=organization_id,
            organization_name=organization_name,
            user_role=user.role,
            user=UserResponse.model_validate(user),
        )
