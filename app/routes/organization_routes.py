"""HTTP routes for organizations."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.controllers.organization_controller import (
    OrganizationAdminEmailExistsError,
    OrganizationController,
    OrganizationNotFoundError,
    OrganizationUserPermissionError,
    OrganizationWelcomeEmailError,
)
from app.dependencies.db import get_db
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationCreateResponse,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.schemas.user import UserCreate, UserResponse

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
    except OrganizationWelcomeEmailError:
        raise HTTPException(
            status_code=502,
            detail="Organization admin welcome email could not be sent",
        ) from None


@router.get("/", response_model=list[OrganizationResponse])
def list_organizations(db: Session = Depends(get_db)) -> list[OrganizationResponse]:
    return OrganizationController.get_all_organizations(db)


@router.post(
    "/{organization_id}/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a user to an organization (admin or superadmin only)",
)
def add_organization_user(
    organization_id: int,
    data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> UserResponse:
    try:
        return OrganizationController.add_user(
            organization_id=organization_id,
            data=data,
            actor_user_id=request.state.user_id,
            actor_role=request.state.user_role,
            db=db,
        )
    except OrganizationNotFoundError:
        raise HTTPException(status_code=404, detail="Organization not found") from None
    except OrganizationUserPermissionError:
        raise HTTPException(
            status_code=403,
            detail="Only this organization's admin or a superadmin can add users",
        ) from None
    except OrganizationAdminEmailExistsError:
        raise HTTPException(status_code=409, detail="User email already exists") from None


@router.get(
    "/{organization_id}/users",
    response_model=list[UserResponse],
    summary="Get users in an organization (member or superadmin only)",
)
def list_organization_users(
    organization_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    try:
        return OrganizationController.get_users(
            organization_id=organization_id,
            actor_user_id=request.state.user_id,
            actor_role=request.state.user_role,
            db=db,
        )
    except OrganizationNotFoundError:
        raise HTTPException(status_code=404, detail="Organization not found") from None
    except OrganizationUserPermissionError:
        raise HTTPException(
            status_code=403,
            detail="Only organization members or a superadmin can view users",
        ) from None


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


@router.delete(
    "/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an organization (superadmin only)",
)
def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
) -> None:
    if not OrganizationController.delete_organization(organization_id, db):
        raise HTTPException(status_code=404, detail="Organization not found")
