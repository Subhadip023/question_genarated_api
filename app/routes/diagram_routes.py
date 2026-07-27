from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.controllers.diagram_controller import (
    DiagramController,
    DiagramNotFoundError,
    DiagramOrganizationNotFoundError,
    DiagramReferenceNotFoundError,
    DiagramTypeValidationError,
)
from app.dependencies.db import get_db
from app.schemas.diagram import DiagramCreate, DiagramResponse

router = APIRouter(prefix="/diagrams", tags=["Diagrams"])


@router.post(
    "/upload",
    response_model=DiagramResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload diagram file and create record",
)
def upload_diagram(
    request: Request,
    file: UploadFile = File(...),
    type: int = Form(..., description="0 for question ref, 1 for question option ref"),
    ref_id: int = Form(..., description="ID of the referred question or option"),
    org_id: int = Form(0, description="Organization ID (0 for default/global)"),
    db: Session = Depends(get_db),
) -> DiagramResponse:
    try:
        diagram = DiagramController.upload_and_create_diagram(
            file=file,
            diagram_type=type,
            ref_id=ref_id,
            org_id=org_id,
            user_id=request.state.user_id,
            db=db,
        )
        return DiagramResponse.model_validate(diagram)
    except DiagramTypeValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    except DiagramOrganizationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except DiagramReferenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None


@router.post(
    "/",
    response_model=DiagramResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a diagram",
)
def create_diagram(
    data: DiagramCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> DiagramResponse:
    try:
        diagram = DiagramController.create_diagram(
            data=data,
            user_id=request.state.user_id,
            db=db,
        )
        return DiagramResponse.model_validate(diagram)
    except DiagramTypeValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    except DiagramOrganizationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except DiagramReferenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None


@router.get(
    "/",
    response_model=list[DiagramResponse],
    summary="List all diagrams",
)
def list_diagrams(db: Session = Depends(get_db)) -> list[DiagramResponse]:
    diagrams = DiagramController.list_diagrams(db)
    return [DiagramResponse.model_validate(diagram) for diagram in diagrams]


@router.get(
    "/{diagram_id}",
    response_model=DiagramResponse,
    summary="Get diagram by ID",
)
def get_diagram(diagram_id: int, db: Session = Depends(get_db)) -> DiagramResponse:
    try:
        diagram = DiagramController.get_diagram(diagram_id, db)
        return DiagramResponse.model_validate(diagram)
    except DiagramNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None


@router.put(
    "/{diagram_id}/upload",
    response_model=DiagramResponse,
    summary="Replace diagram file",
)
def update_diagram_file(
    diagram_id: int,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DiagramResponse:
    try:
        diagram = DiagramController.update_diagram_file(
            diagram_id=diagram_id,
            file=file,
            user_id=request.state.user_id,
            db=db,
        )
        return DiagramResponse.model_validate(diagram)
    except DiagramNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None


@router.delete(
    "/{diagram_id}",
    summary="Delete diagram record and remove file from disk",
)
def delete_diagram(diagram_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        DiagramController.delete_diagram(diagram_id, db)
        return {"detail": f"Diagram #{diagram_id} deleted successfully"}
    except DiagramNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
