"""Authorization rules for organization endpoints."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.database import SessionLocal
from app.models.organization_user import OrganizationUser


class OrganizationPermissionMiddleware(BaseHTTPMiddleware):
    """Allow only superadmins to create organizations."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path.rstrip("/") or "/"
        if request.method == "POST" and path == "/organizations":
            if not self.can_create(getattr(request.state, "user_role", None)):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Only a superadmin can create an organization"},
                )
        if request.method == "PATCH" and path.startswith("/organizations/"):
            try:
                organization_id = int(path.rsplit("/", 1)[1])
            except ValueError:
                return await call_next(request)

            role = getattr(request.state, "user_role", None)
            user_id = getattr(request.state, "user_id", None)
            if role != 0 and not self.is_organization_admin(
                user_id, organization_id, role
            ):
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "Only this organization's admin can update it"
                    },
                )
        return await call_next(request)

    @staticmethod
    def can_create(role: int | None) -> bool:
        """Return whether a role may create an organization."""
        return role == 0

    @staticmethod
    def is_organization_admin(
        user_id: int | None, organization_id: int, role: int | None
    ) -> bool:
        """Check that an admin belongs to the requested organization."""
        if role != 1 or user_id is None:
            return False
        db = SessionLocal()
        try:
            return (
                db.query(OrganizationUser)
                .filter(
                    OrganizationUser.org_id == organization_id,
                    OrganizationUser.user_id == user_id,
                )
                .first()
                is not None
            )
        finally:
            db.close()
