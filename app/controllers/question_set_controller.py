from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.question_set import QuestionSet
from app.models.question_set_question import QuestionSetQuestion
from app.models.organization_user import OrganizationUser
from app.schemas.question_set import QuestionSetCreate
from sqlalchemy import or_


def create_question_set(
        db: Session,
        data: QuestionSetCreate,
        current_user
):

    # role 3 = student
    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot create question sets"
        )


    # Find user's organization
    organization_user = db.query(OrganizationUser).filter(
        OrganizationUser.user_id == current_user.id
    ).first()


    if not organization_user:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to any organization"
        )


    question_set = QuestionSet(

        name=data.name,

        org_id=organization_user.org_id,

        user_id=current_user.id,

        visibility=data.visibility,

        is_active=True

    )


    db.add(question_set)

    db.commit()

    db.refresh(question_set)


    return question_set


from sqlalchemy import or_


def get_question_sets(
        db: Session,
        current_user
):

    # Student cannot view
    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot view question sets"
        )


    # Find user's organization
    organization_user = db.query(OrganizationUser).filter(
        OrganizationUser.user_id == current_user.id
    ).first()


    if not organization_user:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to any organization"
        )


    question_sets = db.query(QuestionSet).filter(
        QuestionSet.is_active == True,
        QuestionSet.visibility == 0
    ).all()


    return question_sets

def get_question_set(
        db: Session,
        set_id: int,
        current_user
):

    # Student cannot access
    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot view question sets"
        )


    organization_user = db.query(OrganizationUser).filter(
        OrganizationUser.user_id == current_user.id
    ).first()


    if not organization_user:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to any organization"
        )


    question_set = db.query(QuestionSet).filter(
        QuestionSet.id == set_id
    ).first()


    if not question_set:
        raise HTTPException(
            status_code=404,
            detail="Question set not found"
        )



    return question_set

def update_question_set(
    db: Session,
    set_id: int,
    data: QuestionSetUpdate,
    current_user
):

    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot update question sets"
        )

    question_set = db.query(QuestionSet).filter(
        QuestionSet.id == set_id
    ).first()

    if not question_set:
        raise HTTPException(
            status_code=404,
            detail="Question set not found"
        )

    if current_user.role not in [0, 1, 2]:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update question sets"
        )

    question_set.name = data.name
    question_set.visibility = data.visibility
    question_set.is_active = data.is_active

    db.commit()
    db.refresh(question_set)

    return question_set

def delete_question_set(
    db: Session,
    set_id: int,
    current_user
):

    # Student cannot delete
    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot delete question sets"
        )

    question_set = db.query(QuestionSet).filter(
        QuestionSet.id == set_id
    ).first()


    if not question_set:
        raise HTTPException(
            status_code=404,
            detail="Question set not found"
        )

    if current_user.role not in [0, 1, 2]:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete question sets"
        )


    db.delete(question_set)
    db.commit()


    return {
        "message": "Question set deleted successfully"
    }

def add_questions_to_set(
    db: Session,
    set_id: int,
    data,
    current_user
):

    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot modify question sets"
        )

    question_set = db.query(QuestionSet).filter(
        QuestionSet.id == set_id
    ).first()


    if not question_set:
        raise HTTPException(
            status_code=404,
            detail="Question set not found"
        )

    if current_user.role not in [0, 1, 2]:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission"
        )

    added_questions = []

    for question_id in data.question_ids:

        exists = db.query(QuestionSetQuestion).filter(
            QuestionSetQuestion.set_id == set_id,
            QuestionSetQuestion.question_id == question_id
        ).first()

        if exists:
            continue

        question = QuestionSetQuestion(
            set_id=set_id,
            question_id=question_id
        )

        db.add(question)

        added_questions.append(question_id)

    db.commit()

    return {
        "message": "Questions added successfully",
        "question_ids": added_questions
    }

def remove_question_from_set(
    db: Session,
    set_id: int,
    question_id: int,
    current_user
):

    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot modify question sets"
        )

    question_set = db.query(QuestionSet).filter(
        QuestionSet.id == set_id
    ).first()

    if not question_set:
        raise HTTPException(
            status_code=404,
            detail="Question set not found"
        )

    if current_user.role not in [0, 1, 2]:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission"
        )

    question_mapping = db.query(QuestionSetQuestion).filter(
        QuestionSetQuestion.set_id == set_id,
        QuestionSetQuestion.question_id == question_id
    ).first()

    if not question_mapping:
        raise HTTPException(
            status_code=404,
            detail="Question is not attached to this set"
        )

    db.delete(question_mapping)

    db.commit()

    return {
        "message": "Question removed from question set successfully"
    }

def copy_question_set(
    db: Session,
    set_id: int,
    current_user
):

    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot copy question sets"
        )

    # Find source set
    source_set = db.query(QuestionSet).filter(
        QuestionSet.id == set_id
    ).first()

    if not source_set:
        raise HTTPException(
            status_code=404,
            detail="Question set not found"
        )

    if source_set.visibility != 0:
        raise HTTPException(
            status_code=403,
            detail="Private question sets cannot be copied"
        )

    organization_user = db.query(OrganizationUser).filter(
        OrganizationUser.user_id == current_user.id
    ).first()

    if not organization_user:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to any organization"
        )

    copied_set = QuestionSet(
        name=source_set.name + " (Copy)",
        org_id=organization_user.org_id,
        user_id=current_user.id,
        visibility=1,   # copied set private
        is_active=True
    )

    db.add(copied_set)

    db.commit()

    db.refresh(copied_set)

    questions = db.query(QuestionSetQuestion).filter(
        QuestionSetQuestion.set_id == set_id
    ).all()

    for item in questions:

        new_question = QuestionSetQuestion(
            set_id=copied_set.id,
            question_id=item.question_id
        )

        db.add(new_question)

    db.commit()

    return {
        "message": "Question set copied successfully",
        "new_set_id": copied_set.id
    }

def get_question_sets_by_org(
    db: Session,
    org_id: int,
    current_user
):

    if current_user.role == 3:
        raise HTTPException(
            status_code=403,
            detail="Students cannot view question sets"
        )

    question_sets = db.query(QuestionSet).filter(
        QuestionSet.org_id == org_id,
        QuestionSet.is_active == True,
        QuestionSet.visibility == 0
    ).all()

    return question_sets