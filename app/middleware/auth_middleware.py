"""Bearer-token authentication middleware.

Hot path: user_id and role are read directly from the signed JWT claims -
zero database queries on every request.

Safety net: a tiny in-memory TTL cache (plain dict + time.time()) checks
that the user still exists in MySQL.  A deleted or banned account will be
rejected within USER_EXISTS_TTL seconds of removal.  No Redis required.
"""

import time
import threading

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.database import SessionLocal
from app.models.user import User
from app.services.auth_service import InvalidTokenError, decode_access_token

# ---------------------------------------------------------------------------
# Lightweight in-memory TTL cache - no external dependencies
# ---------------------------------------------------------------------------
# Structure: { user_id: (exists: bool, cached_at: float) }
# Evicted lazily on access once TTL expires.
_USER_EXISTS_CACHE: dict[int, tuple[bool, float]] = {}
_USER_EXISTS_TTL = 300          # seconds - re-check DB every 5 minutes
_CACHE_LOCK = threading.Lock()  # guards against race on concurrent eviction


def _user_exists(user_id: int) -> bool:
    """Return True if the user_id exists in DB, using a 5-minute TTL cache."""
    now = time.time()

    with _CACHE_LOCK:
        entry = _USER_EXISTS_CACHE.get(user_id)

    if entry is not None:
        exists, cached_at = entry
        if now - cached_at < _USER_EXISTS_TTL:
            return exists  # cache HIT - no DB query

    # Cache MISS or expired -> hit the DB once
    db = SessionLocal()
    try:
        exists = db.query(User.id).filter(User.id == user_id).scalar() is not None
    finally:
        db.close()

    with _CACHE_LOCK:
        _USER_EXISTS_CACHE[user_id] = (exists, now)

    return exists


def invalidate_user_cache(user_id: int) -> None:
    """Call this when a user is deleted or their role changes."""
    with _CACHE_LOCK:
        _USER_EXISTS_CACHE.pop(user_id, None)


class AuthMiddleware(BaseHTTPMiddleware):
    """Require a valid bearer token for non-public API routes."""

    PUBLIC_PATHS = {
        "/",
        "/health",
        "/auth/login",
        "/auth/register",
        "/openapi.json",
        "/student/test-series/invite-info",
    }
    PUBLIC_PREFIXES = ("/docs", "/redoc")
    MAIL_PATHS = {"/mail/send", "/send-mail"}
    MAIL_ALLOWED_ROLES = {0, 1, 2}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path.rstrip("/") or "/"

        authorization = request.headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")
        token_provided = scheme.lower() == "bearer" and bool(token)

        if token_provided:
            try:
                # Hot path: decode the signed JWT - no DB query
                claims = decode_access_token(token)
                user_id = int(claims["sub"])
                user_role = int(claims["role"])

                # Safety net: confirm the account still exists.
                # Uses a 5-minute in-memory TTL cache so the DB is only hit
                # once per user per 5 minutes, not on every request.
                if not _user_exists(user_id):
                    return self._unauthorized("User no longer exists")

                request.state.user_id = user_id
                request.state.user_role = user_role

            except InvalidTokenError as exc:
                return self._unauthorized(str(exc))
            except (KeyError, ValueError):
                return self._unauthorized("Invalid access token")

        is_public = (
            request.method == "OPTIONS"
            or path in self.PUBLIC_PATHS
            or path.startswith(self.PUBLIC_PREFIXES)
            or (request.method == "POST" and path == "/organizations")
        )

        if is_public:
            return await call_next(request)

        if not token_provided or getattr(request.state, "user_id", None) is None:
            return self._unauthorized("Bearer token required")

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
