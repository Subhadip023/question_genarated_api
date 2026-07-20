"""Business logic for organizations."""

import secrets

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.organization import Organization
from app.models.organization_user import OrganizationUser
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationCreateResponse,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import hash_password
from app.services.mail_service import MailService, MailServiceError


class OrganizationAdminEmailExistsError(Exception):
    """Raised when the requested organization admin email already exists."""


class OrganizationNotFoundError(Exception):
    """Raised when an organization does not exist."""


class OrganizationUserPermissionError(Exception):
    """Raised when a user cannot manage an organization's members."""


class OrganizationWelcomeEmailError(Exception):
    """Raised when the initial administrator email cannot be delivered."""


class OrganizationController:
    """Controller responsible for organization operations."""

    @staticmethod
    def create_organization(
        data: OrganizationCreate, db: Session
    ) -> OrganizationCreateResponse:
        temporary_password = secrets.token_urlsafe(12)
        organization = Organization(
            name=data.name.strip(),
            code=OrganizationController._generate_unique_code(db),
            location=data.location.strip() if data.location else None,
            phone_number=data.phone_number.strip() if data.phone_number else None,
            is_active=data.is_active,
        )
        admin = User(
            role=1,
            name=data.admin.name.strip(),
            email=data.admin.email.strip().lower(),
            password=hash_password(temporary_password),
        )
        try:
            db.add(organization)
            db.add(admin)
            db.flush()
            db.add(OrganizationUser(org_id=organization.id, user_id=admin.id))
            MailService.send_mail(
                to_email=admin.email,
                subject="Welcome to QMaster - Your organization account",
                body=(
                    "Welcome to QMaster\n\n"
                    "Your organization has been created.\n\n"
                    f"Organization name: {organization.name}\n"
                    f"Email: {admin.email}\n"
                    f"Temporary password: {temporary_password}\n\n"
                    f"Login: {settings.app_url.rstrip('/')}/login\n\n"
                    "Please reset your password after you log in."
                ),
            )
            db.commit()
            db.refresh(organization)
            db.refresh(admin)
        except MailServiceError as exc:
            db.rollback()
            raise OrganizationWelcomeEmailError from exc
        except IntegrityError as exc:
            db.rollback()
            raise OrganizationAdminEmailExistsError from exc
        except Exception:
            db.rollback()
            raise
        return OrganizationCreateResponse(
            organization=OrganizationResponse.model_validate(organization),
            admin=UserResponse.model_validate(admin),
        )

    @staticmethod
    def _generate_unique_code(db: Session) -> str:
        """Generate an unused six-digit organization code."""
        for _ in range(100):
            code = str(secrets.randbelow(900000) + 100000)
            exists = db.query(Organization.id).filter(Organization.code == code).first()
            if exists is None:
                return code
        raise RuntimeError("Unable to generate a unique organization code")

    @staticmethod
    def get_all_organizations(db: Session) -> list[OrganizationResponse]:
        organizations = db.query(Organization).order_by(Organization.id).all()
        return [OrganizationResponse.model_validate(item) for item in organizations]

    @staticmethod
    def add_user(
        organization_id: int,
        data: UserCreate,
        actor_user_id: int,
        actor_role: int,
        db: Session,
    ) -> UserResponse:
        """Create a user and add them to an organization."""
        organization = db.query(Organization.id).filter(
            Organization.id == organization_id
        ).first()
        if organization is None:
            raise OrganizationNotFoundError

        if actor_role != 0:
            is_admin_member = (
                actor_role == 1
                and db.query(OrganizationUser)
                .filter(
                    OrganizationUser.org_id == organization_id,
                    OrganizationUser.user_id == actor_user_id,
                )
                .first()
                is not None
            )
            if not is_admin_member:
                raise OrganizationUserPermissionError

        user = User(
            role=data.role,
            name=data.name.strip(),
            email=data.email.strip().lower(),
            password=hash_password(data.password),
        )
        try:
            db.add(user)
            db.flush()
            db.add(OrganizationUser(org_id=organization_id, user_id=user.id))
            db.commit()
            db.refresh(user)
        except IntegrityError as exc:
            db.rollback()
            raise OrganizationAdminEmailExistsError from exc
        except Exception:
            db.rollback()
            raise
        return UserResponse.model_validate(user)

    @staticmethod
    def update_organization(
        organization_id: int, data: OrganizationUpdate, db: Session
    ) -> OrganizationResponse | None:
        organization = (
            db.query(Organization)
            .filter(Organization.id == organization_id)
            .first()
        )
        if organization is None:
            return None

        if data.name is not None:
            organization.name = data.name.strip()
        if "location" in data.model_fields_set:
            organization.location = data.location.strip() if data.location else None
        if "phone_number" in data.model_fields_set:
            organization.phone_number = (
                data.phone_number.strip() if data.phone_number else None
            )
        if data.is_active is not None:
            organization.is_active = data.is_active

        try:
            db.commit()
            db.refresh(organization)
        except Exception:
            db.rollback()
            raise
        return OrganizationResponse.model_validate(organization)

    @staticmethod
    def get_organization(
        organization_id: int, db: Session
    ) -> OrganizationResponse | None:
        organization = (
            db.query(Organization)
            .filter(Organization.id == organization_id)
            .first()
        )
        return OrganizationResponse.model_validate(organization) if organization else None

    @staticmethod
    def delete_organization(organization_id: int, db: Session) -> bool:
        """Delete an organization; membership rows cascade at database level."""
        organization = (
            db.query(Organization)
            .filter(Organization.id == organization_id)
            .first()
        )
        if organization is None:
            return False

        try:
            db.delete(organization)
            db.commit()
        except Exception:
            db.rollback()
            raise
        return True
