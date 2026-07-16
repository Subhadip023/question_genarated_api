"""HTTP routes for organizations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.controllers.organization_controller import (
    OrganizationAdminEmailExistsError,
    OrganizationController,
)
from app.dependencies.db import get_db
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationCreateResponse,
    OrganizationResponse,
    OrganizationUpdate,
)

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post(
    "/",
    response_model=OrganizationCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an organization (superadmin only)",
)
def create_organization(
    data: OrganizationCreate, db: Session = Depends(get_db)
) -> OrganizationCreateResponse:
    try:
        return OrganizationController.create_organization(data, db)
    except OrganizationAdminEmailExistsError:
        raise HTTPException(
            status_code=409,
            detail="Admin email already exists",
        ) from None


@router.get("/", response_model=list[OrganizationResponse])
def list_organizations(db: Session = Depends(get_db)) -> list[OrganizationResponse]:
    return OrganizationController.get_all_organizations(db)


@router.patch(
    "/{organization_id}",
    response_model=OrganizationResponse,
    summary="Update an organization (organization admin only)",
)
def update_organization(
    organization_id: int,
    data: OrganizationUpdate,
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    organization = OrganizationController.update_organization(
        organization_id, data, db
    )
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(
    organization_id: int, db: Session = Depends(get_db)
) -> OrganizationResponse:
    organization = OrganizationController.get_organization(organization_id, db)
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization
