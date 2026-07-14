"""
Application entry point.
Wires FastAPI app with all routers following MVC structure.
"""

import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routes import health_routes, question_routes, question_option_routes

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
