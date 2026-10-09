"""Authenticated test-series management routes."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, UploadFile, File
from sqlalchemy.orm import Session

from app.controllers.test_series_controller import (
    TestSeriesController,
    TestSeriesHasAttemptsError,
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
from app.schemas.user import PaginatedUserResponse

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
    except Exception as exc:
        import traceback
        print(f"Error fetching results for test series {series_id}: {exc}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error fetching test series results: {str(exc)}") from None


@router.post("/{series_id}/result-sheet")
def upload_result_sheet(
    series_id: int,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        return TestSeriesController.upload_result_sheet(
            series_id, file, request.state.user_id, request.state.user_role, db
        )
    except TestSeriesPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from None
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to upload result sheet: {str(exc)}") from None


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
    try:
        return TestSeriesController.list_for_user(
            request.state.user_id, request.state.user_role, db
        )
    except Exception as exc:
        import traceback
        raise HTTPException(status_code=500, detail=f"Error listing test series: {str(exc)}\n{traceback.format_exc()}") from None



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


@router.delete("/{series_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_series(
    series_id: int, request: Request, db: Session = Depends(get_db)
) -> None:
    try:
        if not TestSeriesController.delete(series_id, request.state.user_id, db):
            raise HTTPException(status_code=404, detail="Test series not found")
    except TestSeriesPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from None
    except TestSeriesHasAttemptsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None

@router.get("/{series_id}/questions")
def get_test_series_questions(
    series_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        result = TestSeriesController.get_questions_with_answers(
            series_id,
            request.state.user_id,
            request.state.user_role,
            db
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Test series not found"
            )

        return result

    except TestSeriesPermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc)
        ) from None


@router.get("/{series_id}/question-paper-pdf")
def get_test_series_question_paper_pdf(
    series_id: int,
    request: Request,
    include_answers: bool = False,
    show_answer_key: bool | None = None,
    columns: int = 1,
    font_size: str = "normal",
    fontSize: str | None = None,
    show_candidate_box: bool = True,
    showCandidateBox: bool | None = None,
    show_instructions: bool = True,
    showInstructions: bool | None = None,
    show_org_header: bool = True,
    showOrgHeader: bool | None = None,
    db: Session = Depends(get_db),
):
    try:
        final_include_answers = show_answer_key if show_answer_key is not None else include_answers
        final_font_size = fontSize if fontSize is not None else font_size
        final_show_candidate_box = showCandidateBox if showCandidateBox is not None else show_candidate_box
        final_show_instructions = showInstructions if showInstructions is not None else show_instructions
        final_show_org_header = showOrgHeader if showOrgHeader is not None else show_org_header
        final_columns = 2 if int(columns or 1) == 2 else 1

        pdf_bytes, filename = TestSeriesController.generate_question_paper_pdf(
            series_id=series_id,
            user_id=request.state.user_id,
            user_role=request.state.user_role,
            db=db,
            include_answers=final_include_answers,
            columns=final_columns,
            font_size=final_font_size,
            show_candidate_box=final_show_candidate_box,
            show_instructions=final_show_instructions,
            show_org_header=final_show_org_header,
        )

        if not pdf_bytes:
            raise HTTPException(
                status_code=404,
                detail="Test series not found"
            )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{filename}"',
                "Content-Type": "application/pdf",
            },
        )

    except TestSeriesPermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc)
        ) from None


@router.get("/{series_id}/students", response_model=PaginatedUserResponse)
def get_test_series_students(
    series_id: int,
    request: Request,
    page: int = 1,
    limit: int = 5,
    sort_order: str = "desc",
    q: str | None = None,
    exclude_batch_ids: str | None = None,
    db: Session = Depends(get_db),
) -> PaginatedUserResponse:
    try:
        parsed_exclude_batch_ids = None
        if exclude_batch_ids is not None:
            parsed_exclude_batch_ids = []
            for part in exclude_batch_ids.split(","):
                part = part.strip()
                if part.isdigit() and int(part) > 0:
                    parsed_exclude_batch_ids.append(int(part))

        return TestSeriesController.get_eligible_students(
            series_id=series_id,
            user_id=request.state.user_id,
            user_role=request.state.user_role,
            db=db,
            page=page,
            limit=limit,
            sort_order=sort_order,
            q=q,
            exclude_batch_ids=parsed_exclude_batch_ids,
        )
    except TestSeriesPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from None
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Error fetching test series students: {str(exc)}"
        ) from None