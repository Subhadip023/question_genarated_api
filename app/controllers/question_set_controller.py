from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.question_set import QuestionSet
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