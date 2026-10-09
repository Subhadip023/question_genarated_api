import hashlib
import secrets
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_

from app.models.question_set import QuestionSet
from app.models.question_set_question import QuestionSetQuestion
from app.models.organization_user import OrganizationUser
from app.models.question import Question
from app.models.diagram import Diagram
from app.models.test_series import TestSeries
from app.models.series_question import SeriesQuestion
from app.schemas.question_set import (
    QuestionSetCreate,
    QuestionSetUpdate,
    AddQuestionsRequest,
    ConvertToTestSeriesRequest,
)


def create_question_set(
    db: Session,
    data: QuestionSetCreate,
    current_user,
):
    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot create question sets",
        )

    organization_user = (
        db.query(OrganizationUser)
        .filter(OrganizationUser.user_id == current_user.id)
        .first()
    )

    org_id = organization_user.org_id if organization_user else (0 if current_user.role == 0 else None)
    if org_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to any organization",
        )

    question_set = QuestionSet(
        name=data.name.strip(),
        org_id=org_id,
        user_id=current_user.id,
        visibility=data.visibility,
        is_active=True,
    )

    db.add(question_set)
    db.commit()
    db.refresh(question_set)

    return {
        "id": question_set.id,
        "name": question_set.name,
        "org_id": question_set.org_id,
        "user_id": question_set.user_id,
        "is_active": question_set.is_active,
        "visibility": question_set.visibility,
        "question_count": 0,
    }


def get_question_sets(
    db: Session,
    current_user,
):
    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot view question sets",
        )

    organization_user = (
        db.query(OrganizationUser)
        .filter(OrganizationUser.user_id == current_user.id)
        .first()
    )
    org_id = organization_user.org_id if organization_user else (0 if current_user.role == 0 else None)

    query = db.query(QuestionSet).filter(QuestionSet.is_active.is_(True))

    if current_user.role == 0:
        pass  # Super admin sees all
    elif org_id is not None:
        query = query.filter(
            or_(
                QuestionSet.visibility == 1,  # Public
                QuestionSet.org_id == org_id,  # Organization only
                QuestionSet.user_id == current_user.id,  # Creator
            )
        )
    else:
        query = query.filter(
            or_(
                QuestionSet.visibility == 1,
                QuestionSet.user_id == current_user.id,
            )
        )

    sets = query.order_by(QuestionSet.id.desc()).all()
    set_ids = [s.id for s in sets]

    counts = {}
    if set_ids:
        counts_query = (
            db.query(QuestionSetQuestion.set_id, func.count(QuestionSetQuestion.id))
            .filter(QuestionSetQuestion.set_id.in_(set_ids))
            .group_by(QuestionSetQuestion.set_id)
            .all()
        )
        counts = {r[0]: r[1] for r in counts_query}

    return [
        {
            "id": s.id,
            "name": s.name,
            "org_id": s.org_id,
            "user_id": s.user_id,
            "is_active": s.is_active,
            "visibility": s.visibility,
            "question_count": counts.get(s.id, 0),
        }
        for s in sets
    ]


def get_question_set(
    db: Session,
    set_id: int,
    current_user,
):
    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot view question sets",
        )

    question_set = db.query(QuestionSet).filter(QuestionSet.id == set_id).first()
    if not question_set:
        raise HTTPException(
            status_code=404,
            detail="Question set not found",
        )

    organization_user = (
        db.query(OrganizationUser)
        .filter(OrganizationUser.user_id == current_user.id)
        .first()
    )
    org_id = organization_user.org_id if organization_user else (0 if current_user.role == 0 else None)

    if current_user.role != 0 and question_set.visibility != 1:
        if org_id is not None and question_set.org_id != org_id and question_set.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied to this private question set",
            )

    set_questions = (
        db.query(QuestionSetQuestion, Question)
        .join(Question, QuestionSetQuestion.question_id == Question.id)
        .options(joinedload(Question.options), joinedload(Question.topic))
        .filter(QuestionSetQuestion.set_id == set_id)
        .order_by(QuestionSetQuestion.id.asc())
        .all()
    )

    q_ids = [q.id for _, q in set_questions]
    diagrams_map = {}
    if q_ids:
        diagrams = (
            db.query(Diagram)
            .filter(Diagram.type == 0, Diagram.ref_id.in_(q_ids))
            .all()
        )
        for d in diagrams:
            diagrams_map[d.ref_id] = d.path

    questions_list = []
    for sq, q in set_questions:
        questions_list.append({
            "set_question_id": sq.id,
            "id": q.id,
            "question": q.question,
            "marks": float(q.marks),
            "topic_id": q.topic_id,
            "topic_name": q.topic.name if q.topic else None,
            "diagram_path": diagrams_map.get(q.id),
            "is_global": q.is_global,
            "options": [
                {
                    "id": o.id,
                    "ans": o.ans,
                    "is_correct": o.is_correct,
                }
                for o in q.options
            ],
        })

    return {
        "id": question_set.id,
        "name": question_set.name,
        "org_id": question_set.org_id,
        "user_id": question_set.user_id,
        "is_active": question_set.is_active,
        "visibility": question_set.visibility,
        "question_count": len(questions_list),
        "questions": questions_list,
    }


def update_question_set(
    db: Session,
    set_id: int,
    data: QuestionSetUpdate,
    current_user,
):
    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot update question sets",
        )

    question_set = db.query(QuestionSet).filter(QuestionSet.id == set_id).first()
    if not question_set:
        raise HTTPException(
            status_code=404,
            detail="Question set not found",
        )

    organization_user = (
        db.query(OrganizationUser)
        .filter(OrganizationUser.user_id == current_user.id)
        .first()
    )
    org_id = organization_user.org_id if organization_user else (0 if current_user.role == 0 else None)

    if current_user.role != 0 and question_set.user_id != current_user.id and (org_id is None or question_set.org_id != org_id):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update this question set",
        )

    if data.name is not None:
        question_set.name = data.name.strip()
    if data.visibility is not None:
        question_set.visibility = data.visibility
    if data.is_active is not None:
        question_set.is_active = data.is_active

    db.commit()
    db.refresh(question_set)

    return {
        "id": question_set.id,
        "name": question_set.name,
        "org_id": question_set.org_id,
        "user_id": question_set.user_id,
        "is_active": question_set.is_active,
        "visibility": question_set.visibility,
    }


def delete_question_set(
    db: Session,
    set_id: int,
    current_user,
):
    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot delete question sets",
        )

    question_set = db.query(QuestionSet).filter(QuestionSet.id == set_id).first()
    if not question_set:
        raise HTTPException(
            status_code=404,
            detail="Question set not found",
        )

    organization_user = (
        db.query(OrganizationUser)
        .filter(OrganizationUser.user_id == current_user.id)
        .first()
    )
    org_id = organization_user.org_id if organization_user else (0 if current_user.role == 0 else None)

    if current_user.role != 0 and question_set.user_id != current_user.id and (org_id is None or question_set.org_id != org_id):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete this question set",
        )

    db.delete(question_set)
    db.commit()

    return {"message": "Question set deleted successfully"}


def add_questions_to_set(
    db: Session,
    set_id: int,
    data: AddQuestionsRequest,
    current_user,
):
    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot modify question sets",
        )

    question_set = db.query(QuestionSet).filter(QuestionSet.id == set_id).first()
    if not question_set:
        raise HTTPException(
            status_code=404,
            detail="Question set not found",
        )

    added_questions = []
    for question_id in data.question_ids:
        exists = (
            db.query(QuestionSetQuestion)
            .filter(
                QuestionSetQuestion.set_id == set_id,
                QuestionSetQuestion.question_id == question_id,
            )
            .first()
        )
        if exists:
            continue

        q = QuestionSetQuestion(set_id=set_id, question_id=question_id)
        db.add(q)
        added_questions.append(question_id)

    db.commit()

    return {
        "message": f"Added {len(added_questions)} questions to set",
        "question_ids": added_questions,
    }


def remove_question_from_set(
    db: Session,
    set_id: int,
    question_id: int,
    current_user,
):
    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot modify question sets",
        )

    question_set = db.query(QuestionSet).filter(QuestionSet.id == set_id).first()
    if not question_set:
        raise HTTPException(
            status_code=404,
            detail="Question set not found",
        )

    mapping = (
        db.query(QuestionSetQuestion)
        .filter(
            QuestionSetQuestion.set_id == set_id,
            QuestionSetQuestion.question_id == question_id,
        )
        .first()
    )
    if not mapping:
        raise HTTPException(
            status_code=404,
            detail="Question is not in this question set",
        )

    db.delete(mapping)
    db.commit()

    return {"message": "Question removed from set"}


def copy_question_set(
    db: Session,
    set_id: int,
    current_user,
):
    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot copy question sets",
        )

    original_set = db.query(QuestionSet).filter(QuestionSet.id == set_id).first()
    if not original_set:
        raise HTTPException(
            status_code=404,
            detail="Question set not found",
        )

    organization_user = (
        db.query(OrganizationUser)
        .filter(OrganizationUser.user_id == current_user.id)
        .first()
    )
    org_id = organization_user.org_id if organization_user else (0 if current_user.role == 0 else original_set.org_id)

    new_set = QuestionSet(
        name=f"{original_set.name} (Copy)",
        org_id=org_id,
        user_id=current_user.id,
        visibility=original_set.visibility,
        is_active=True,
    )
    db.add(new_set)
    db.flush()

    original_questions = (
        db.query(QuestionSetQuestion)
        .filter(QuestionSetQuestion.set_id == set_id)
        .all()
    )
    for oq in original_questions:
        db.add(QuestionSetQuestion(set_id=new_set.id, question_id=oq.question_id))

    db.commit()
    db.refresh(new_set)

    return {
        "id": new_set.id,
        "name": new_set.name,
        "org_id": new_set.org_id,
        "user_id": new_set.user_id,
        "is_active": new_set.is_active,
        "visibility": new_set.visibility,
        "question_count": len(original_questions),
    }


def get_question_sets_by_org(
    db: Session,
    org_id: int,
    current_user,
):
    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot view question sets",
        )

    query = db.query(QuestionSet).filter(
        QuestionSet.is_active.is_(True),
        QuestionSet.org_id == org_id,
    )
    sets = query.order_by(QuestionSet.id.desc()).all()
    return sets


def convert_to_test_series(
    db: Session,
    set_id: int,
    data: ConvertToTestSeriesRequest,
    current_user,
):
    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot create test series",
        )

    question_set = db.query(QuestionSet).filter(QuestionSet.id == set_id).first()
    if not question_set:
        raise HTTPException(
            status_code=404,
            detail="Question set not found",
        )

    set_questions = (
        db.query(QuestionSetQuestion, Question)
        .join(Question, QuestionSetQuestion.question_id == Question.id)
        .filter(QuestionSetQuestion.set_id == set_id)
        .order_by(QuestionSetQuestion.id.asc())
        .all()
    )

    if not set_questions:
        raise HTTPException(
            status_code=400,
            detail="Cannot create a test series from an empty question set. Add questions first.",
        )

    from app.controllers.test_series_controller import TestSeriesController
    series_code = TestSeriesController._generate_unique_code(db)
    invite_token = secrets.token_urlsafe(16)
    invite_token_hash = hashlib.sha256(invite_token.encode()).hexdigest()

    series_name = data.name.strip() if data.name and data.name.strip() else question_set.name

    test_series = TestSeries(
        code=series_code,
        invite_token=invite_token,
        invite_token_hash=invite_token_hash,
        access_type=data.access_type,
        name=series_name,
        org_id=question_set.org_id or 0,
        created_by=current_user.id,
        duration_seconds=data.duration_minutes * 60,
        valid_until=data.valid_until,
        is_active=True,
        is_result_show=False,
        is_score_show=False,
    )

    db.add(test_series)
    db.flush()

    for idx, (_, q) in enumerate(set_questions):
        sq = SeriesQuestion(
            series_id=test_series.id,
            question_id=q.id,
            marks=float(q.marks),
            negative_marks=0.0,
            position=idx + 1,
        )
        db.add(sq)

    db.commit()
    db.refresh(test_series)

    return {
        "id": test_series.id,
        "name": test_series.name,
        "code": test_series.code,
        "access_type": test_series.access_type,
        "question_count": len(set_questions),
        "message": f"Successfully created test series '{test_series.name}' with {len(set_questions)} questions",
    }