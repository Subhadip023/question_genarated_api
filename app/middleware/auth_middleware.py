"""Bearer-token authentication middleware."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.database import SessionLocal
from app.models.user import User
from app.services.auth_service import InvalidTokenError, decode_access_token


class AuthMiddleware(BaseHTTPMiddleware):
    """Require a valid bearer token for non-public API routes."""

    PUBLIC_PATHS = {
        "/",
        "/health",
        "/auth/login",
        "/auth/register",
        "/openapi.json",
    }
    PUBLIC_PREFIXES = ("/docs", "/redoc")
    MAIL_PATHS = {"/mail/send", "/send-mail"}
    MAIL_ALLOWED_ROLES = {0, 1, 2}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path.rstrip("/") or "/"
        if (
            request.method == "OPTIONS"
            or path in self.PUBLIC_PATHS
            or path.startswith(self.PUBLIC_PREFIXES)
        ):
            return await call_next(request)

        authorization = request.headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return self._unauthorized("Bearer token required")

        try:
            claims = decode_access_token(token)
            user_id = int(claims["sub"])
        except InvalidTokenError as exc:
            return self._unauthorized(str(exc))

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user is None:
                return self._unauthorized("User no longer exists")
            request.state.user_id = user.id
            request.state.user_role = user.role
        finally:
            db.close()

        if (
            path in self.MAIL_PATHS
            and request.state.user_role not in self.MAIL_ALLOWED_ROLES
        ):
            return self._forbidden("Only roles 0, 1, and 2 can send mail")

        return await call_next(request)

    @staticmethod
    def _unauthorized(detail: str) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": detail},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @staticmethod
    def _forbidden(detail: str) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": detail})
