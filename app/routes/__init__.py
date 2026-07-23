"""Routes package — exports all application routers."""

from app.routes import (
    auth_routes,
    diagram_routes,
    health_routes,
    mail_routes,
    organization_routes,
    question_option_routes,
    question_routes,
    student_test_routes,
    test_series_routes,
    topic_routes,
    user_routes,
)

__all__ = [
    "auth_routes",
    "diagram_routes",
    "health_routes",
    "mail_routes",
    "organization_routes",
    "question_routes",
    "question_option_routes",
    "student_test_routes",
    "test_series_routes",
    "topic_routes",
    "user_routes",
]
