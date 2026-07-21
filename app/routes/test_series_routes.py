"""Authenticated test-series management routes."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.controllers.test_series_controller import (
    TestSeriesController,
    TestSeriesPermissionError,
    TestSeriesQuestionError,
)
from app.dependencies.db import get_db
from app.schemas.test_series import (
    TestSeriesCreate,
    TestSeriesResponse,
    TestSeriesResultsResponse,
    TestSeriesUpdate,
)

router = APIRouter(prefix="/test-series", tags=["Test Series"])


@router.get("/{series_id}/results", response_model=TestSeriesResultsResponse)
def get_test_series_results(
    series_id: int, request: Request, db: Session = Depends(get_db)
) -> TestSeriesResultsResponse:
    try:
        return TestSeriesController.get_results(
            series_id, request.state.user_id, request.state.user_role, db
        )
    except TestSeriesPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from None



@router.post("/", response_model=TestSeriesResponse, status_code=status.HTTP_201_CREATED)
def create_test_series(
    data: TestSeriesCreate, request: Request, db: Session = Depends(get_db)
) -> TestSeriesResponse:
    try:
        return TestSeriesController.create(
            data, request.state.user_id, request.state.user_role, db
        )
    except TestSeriesPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from None
    except TestSeriesQuestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None


@router.get("/", response_model=list[TestSeriesResponse])
def list_test_series(
    request: Request, db: Session = Depends(get_db)
) -> list[TestSeriesResponse]:
    return TestSeriesController.list_for_user(
        request.state.user_id, request.state.user_role, db
    )


@router.get("/{series_id}", response_model=TestSeriesResponse)
def get_test_series(
    series_id: int, request: Request, db: Session = Depends(get_db)
) -> TestSeriesResponse:
    result = TestSeriesController.get_for_user(
        series_id, request.state.user_id, request.state.user_role, db
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Test series not found")
    return result


@router.patch("/{series_id}", response_model=TestSeriesResponse)
def update_test_series(
    series_id: int,
    data: TestSeriesUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> TestSeriesResponse:
    try:
        result = TestSeriesController.update(
            series_id, data, request.state.user_id, request.state.user_role, db
        )
        if result is None:
            raise HTTPException(status_code=404, detail="Test series not found")
        return result
    except TestSeriesPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from None
    except TestSeriesQuestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None

