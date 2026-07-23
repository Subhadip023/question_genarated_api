from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.controllers.diagram_controller import (
    DiagramController,
    DiagramOrganizationNotFoundError,
    DiagramReferenceNotFoundError,
    DiagramTypeValidationError,
)
from app.dependencies.db import get_db
from app.schemas.diagram import DiagramCreate, DiagramResponse

router = APIRouter(prefix="/diagrams", tags=["Diagrams"])


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
