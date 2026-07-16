"""Student registration-independent test-taking endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.controllers.student_test_controller import (
    StudentTestController,
    StudentTestPermissionError,
    StudentTestValidationError,
)
from app.dependencies.db import get_db
from app.schemas.student_test import (
    AttemptHistoryResponse,
    AttemptResponse,
    AvailableSeriesResponse,
    SaveAnswerRequest,
    StartAttemptRequest,
)


router = APIRouter(prefix="/student", tags=["Student Tests"])


def _call(action):
    try:
        return action()
    except StudentTestPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from None
    except StudentTestValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None


@router.get("/test-series", response_model=list[AvailableSeriesResponse])
def list_public_tests(
    request: Request, db: Session = Depends(get_db)
) -> list[AvailableSeriesResponse]:
    return _call(lambda: StudentTestController.list_public(request.state.user_role, db))


@router.post("/test-series/start", response_model=AttemptResponse, status_code=201)
def start_test(
    data: StartAttemptRequest, request: Request, db: Session = Depends(get_db)
) -> AttemptResponse:
    return _call(
        lambda: StudentTestController.start(
            data, request.state.user_id, request.state.user_role, db
        )
    )


@router.put(
    "/attempts/{attempt_id}/questions/{attempt_question_id}",
    response_model=AttemptResponse,
)
def save_answer(
    attempt_id: int,
    attempt_question_id: int,
    data: SaveAnswerRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> AttemptResponse:
    return _call(
        lambda: StudentTestController.save_answer(
            attempt_id,
            attempt_question_id,
            data.selected_option_id,
            request.state.user_id,
            request.state.user_role,
            db,
        )
    )


@router.post("/attempts/{attempt_id}/submit", response_model=AttemptResponse)
def submit_attempt(
    attempt_id: int, request: Request, db: Session = Depends(get_db)
) -> AttemptResponse:
    return _call(
        lambda: StudentTestController.submit(
            attempt_id, request.state.user_id, request.state.user_role, db
        )
    )


@router.get("/attempts/{attempt_id}", response_model=AttemptResponse)
def get_attempt(
    attempt_id: int, request: Request, db: Session = Depends(get_db)
) -> AttemptResponse:
    return _call(
        lambda: StudentTestController.get_attempt(
            attempt_id, request.state.user_id, request.state.user_role, db
        )
    )


@router.get("/attempt-history", response_model=list[AttemptHistoryResponse])
def attempt_history(
    request: Request, db: Session = Depends(get_db)
) -> list[AttemptHistoryResponse]:
    return _call(
        lambda: StudentTestController.history(
            request.state.user_id, request.state.user_role, db
        )
    )
