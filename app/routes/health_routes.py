"""
Health / root routes — system-level endpoints.
"""

from fastapi import APIRouter

from app.controllers.question_controller import QuestionController

router = APIRouter(tags=["Health"])


@router.get("/", summary="Welcome")
def read_root() -> dict:
    return QuestionController.get_welcome()


@router.get("/health", summary="Health check")
def health_check() -> dict:
    return QuestionController.get_health()
