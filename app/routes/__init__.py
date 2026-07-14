"""Routes package — exports all application routers."""

from app.routes import health_routes, question_routes, question_option_routes

__all__ = ["health_routes", "question_routes", "question_option_routes"]
