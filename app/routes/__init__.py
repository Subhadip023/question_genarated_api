"""Routes package — exports all application routers."""

from app.routes import (
    auth_routes,
    health_routes,
    organization_routes,
    question_option_routes,
    question_routes,
    user_routes,
)

__all__ = [
    "auth_routes",
    "health_routes",
    "organization_routes",
    "question_routes",
    "question_option_routes",
    "user_routes",
]
