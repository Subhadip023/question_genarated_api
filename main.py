"""
Application entry point.
Wires FastAPI app with all routers following MVC structure.
"""

import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.organization_permission_middleware import (
    OrganizationPermissionMiddleware,
)
from app.routes import (
    auth_routes,
    health_routes,
    organization_routes,
    question_option_routes,
    question_routes,
    student_test_routes,
    test_series_routes,
    user_routes,
)

# Configure logging so errors print to console with full tracebacks
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Question Generator API",
    description="A FastAPI application structured using MVC (Model-View-Controller).",
    version="0.1.0",
)

# Starlette executes the last registered middleware first. Authentication must
# populate request.state before organization permissions are checked.
app.add_middleware(OrganizationPermissionMiddleware)
app.add_middleware(AuthMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and return the real error detail."""
    tb = traceback.format_exc()
    logger.error("Unhandled exception on %s %s:\n%s", request.method, request.url, tb)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": tb},
    )


# Register routers
app.include_router(health_routes.router)
app.include_router(question_routes.router)
app.include_router(question_option_routes.router)
app.include_router(test_series_routes.router)
app.include_router(student_test_routes.router)
app.include_router(user_routes.router)
app.include_router(auth_routes.router)
app.include_router(organization_routes.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
