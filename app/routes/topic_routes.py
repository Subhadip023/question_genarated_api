from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.controllers.topic_controller import (
    TopicController,
    TopicPermissionError,
)
from app.dependencies.db import get_db
from app.schemas.topic import (
    TopicCreate,
    TopicResponse,
    TopicUpdate,
)

router = APIRouter(prefix="/topics", tags=["Topics"])


@router.post(
    "/",
    response_model=TopicResponse,
    status_code=201,
    summary="Create a topic",
    description="Create a new topic associated with organization (roles 0-2).",
)
def create_topic(
    data: TopicCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> TopicResponse:
    try:
        return TopicController.create_topic(
            data,
            user_id=request.state.user_id,
            user_role=request.state.user_role,
            db=db,
        )
    except TopicPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))


@router.get(
    "/",
    response_model=list[TopicResponse],
    summary="List all topics",
    description="Get all topics visible to the authenticated user.",
)
def list_topics(
    request: Request,
    db: Session = Depends(get_db),
) -> list[TopicResponse]:
    return TopicController.get_all_topics(
        user_id=request.state.user_id,
        user_role=request.state.user_role,
        db=db,
    )


@router.get(
    "/{topic_id}",
    response_model=TopicResponse,
    summary="Get topic by ID",
)
def get_topic(
    topic_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> TopicResponse:
    topic = TopicController.get_topic(
        topic_id,
        user_id=request.state.user_id,
        user_role=request.state.user_role,
        db=db,
    )
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found or access denied")
    return topic


@router.patch(
    "/{topic_id}",
    response_model=TopicResponse,
    summary="Update a topic",
)
def update_topic(
    topic_id: int,
    data: TopicUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> TopicResponse:
    try:
        topic = TopicController.update_topic(
            topic_id,
            data,
            user_id=request.state.user_id,
            user_role=request.state.user_role,
            db=db,
        )
        if topic is None:
            raise HTTPException(status_code=404, detail="Topic not found")
        return topic
    except TopicPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))


@router.delete(
    "/{topic_id}",
    summary="Delete a topic",
)
def delete_topic(
    topic_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        deleted = TopicController.delete_topic(
            topic_id,
            user_id=request.state.user_id,
            user_role=request.state.user_role,
            db=db,
        )
        if not deleted:
            raise HTTPException(status_code=404, detail="Topic not found")
        return {"detail": "Topic deleted"}
    except TopicPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
