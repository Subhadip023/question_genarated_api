from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.controllers.answer_key_controller import AnswerKeyController
from app.schemas.answer_key import AnswerKeyResponse


router = APIRouter(
    prefix="/test-series",
    tags=["Answer Key"]
)


@router.get(
    "/{series_id}/result-sheet",
    response_model=AnswerKeyResponse
)
def get_result_sheet(
    series_id: int,
    db: Session = Depends(get_db)
):
    answer_key = AnswerKeyController.get(
        series_id,
        db
    )

    if not answer_key:
        raise HTTPException(
            status_code=404,
            detail="Result sheet not found"
        )

    return answer_key


@router.post(
    "/{series_id}/result-sheet",
    response_model=AnswerKeyResponse
)
def upload_result_sheet(
    series_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        answer_key = AnswerKeyController.create(
            series_id,
            file,
            db
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if not answer_key:
        raise HTTPException(
            status_code=404,
            detail="Test series not found"
        )

    return answer_key


@router.delete(
    "/{series_id}/result-sheet"
)
def delete_result_sheet(
    series_id: int,
    db: Session = Depends(get_db)
):
    deleted = AnswerKeyController.delete(
        series_id,
        db
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Result sheet not found"
        )

    return {
        "message": "Result sheet deleted successfully"
    }
    