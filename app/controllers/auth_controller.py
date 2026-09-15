"""Authentication controller."""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.organization import Organization
from app.models.organization_user import OrganizationUser
from app.models.user import User
from app.schemas.user import (
    LoginRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    StudentRegister,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import create_access_token, hash_password, verify_password
from app.services.cache_service import (
    cache_user,
    get_user_by_email,
    delete_user_cache,
)


class InvalidCredentialsError(Exception):
    """Raised when login credentials are incorrect."""


class AccountDeactivatedError(Exception):
    """Raised when an organization account is deactivated."""


class EmailAlreadyExistsError(Exception):
    """Raised when a registration email is already used."""


class InvalidOldPasswordError(Exception):
    """Raised when the supplied current password is incorrect."""


class PasswordConfirmationError(Exception):
    """Raised when the new password and its confirmation differ."""


class AuthController:
    @staticmethod
    def register_student(
        data: StudentRegister,
        db: Session
    ) -> UserResponse:

        student = User(
            role=3,
            name=data.name.strip(),
            email=data.email.strip().lower(),
            password=hash_password(data.password),
        )

        try:
            db.add(student)
            db.commit()
            db.refresh(student)

            # Store in Redis
            cache_user(student)

        except IntegrityError as exc:
            db.rollback()
            raise EmailAlreadyExistsError from exc

        return UserResponse.model_validate(student)

    @staticmethod
    def login(data: LoginRequest, db: Session) -> TokenResponse:
        email = data.email.strip().lower()

        cached_user = get_user_by_email(email)

        if cached_user:
            print(f"REDIS HIT: {email}")
            # Redis HIT
            user_id = cached_user["id"]
            user_role = cached_user["role"]
            user_name = cached_user["name"]
            user_email = cached_user["email"]
            user_password = cached_user["password"]
            created_at = datetime.fromisoformat(
                cached_user["created_at"]
            )
            updated_at = datetime.fromisoformat(
                cached_user["updated_at"]
            )

        else:
            print(f"REDIS MISS: {email}")
            # Redis MISS -> Get user from MySQL
            user = (
                db.query(User)
                .filter(User.email == email)
                .first()
            )

            if user is None:
                raise InvalidCredentialsError

            # Store user in Redis
            cache_user(user)

            user_id = user.id
            user_role = user.role
            user_name = user.name
            user_email = user.email
            user_password = user.password
            created_at = user.created_at
            updated_at = user.updated_at

        # Verify password
        if not verify_password(data.password, user_password):
            raise InvalidCredentialsError

        # Organization check
        if user_role == 0:
            organization_id = 0
            organization_name = "Global"

        else:
            organization = (
                db.query(Organization)
                .join(
                    OrganizationUser,
                    OrganizationUser.org_id == Organization.id
                )
                .filter(
                    OrganizationUser.user_id == user_id
                )
                .order_by(Organization.id)
                .first()
            )

            if organization and not organization.is_active:
                raise AccountDeactivatedError(
                    "Account is not active, Contact to super admin"
                )

            organization_id = (
                organization.id
                if organization
                else None
            )

            organization_name = (
                organization.name
                if organization
                else None
            )

        token, expires_in = create_access_token(
            user_id,
            user_role
        )

        user_response = UserResponse(
            id=user_id,
            role=user_role,
            name=user_name,
            email=user_email,
            created_at=created_at,
            updated_at=updated_at,
        )

        return TokenResponse(
            message=f"Welcome, {user_name}!",
            access_token=token,
            expires_in=expires_in,
            organization_id=organization_id,
            organization_name=organization_name,
            user_role=user_role,
            user=user_response,
        )

    @staticmethod
    def reset_password(
        user_id: int,
        data: ResetPasswordRequest,
        db: Session
    ) -> ResetPasswordResponse:

        if data.new_password != data.confirm_new_password:
            raise PasswordConfirmationError

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None or not verify_password(
            data.old_password,
            user.password
        ):
            raise InvalidOldPasswordError

        user.password = hash_password(
            data.new_password
        )

        try:
            db.commit()
            db.refresh(user)

            # Update Redis
            cache_user(user)

        except Exception:
            db.rollback()
            raise

        return ResetPasswordResponse()
