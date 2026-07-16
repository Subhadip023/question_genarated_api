"""Business logic for organizations."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.organization_user import OrganizationUser
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationCreateResponse,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.schemas.user import UserResponse
from app.services.auth_service import hash_password


class OrganizationAdminEmailExistsError(Exception):
    """Raised when the requested organization admin email already exists."""


class OrganizationController:
    """Controller responsible for organization operations."""

    @staticmethod
    def create_organization(
        data: OrganizationCreate, db: Session
    ) -> OrganizationCreateResponse:
        organization = Organization(
            name=data.name.strip(),
            is_active=data.is_active,
        )
        admin = User(
            role=1,
            name=data.admin.name.strip(),
            email=data.admin.email.strip().lower(),
            password=hash_password(data.admin.password),
        )
        try:
            db.add(organization)
            db.add(admin)
            db.flush()
            db.add(OrganizationUser(org_id=organization.id, user_id=admin.id))
            db.commit()
            db.refresh(organization)
            db.refresh(admin)
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
    def get_all_organizations(db: Session) -> list[OrganizationResponse]:
        organizations = db.query(Organization).order_by(Organization.id).all()
        return [OrganizationResponse.model_validate(item) for item in organizations]

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
