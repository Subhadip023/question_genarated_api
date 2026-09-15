from datetime import datetime

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization_user import OrganizationUser
from app.database import get_db
from app.services.auth_service import decode_access_token
from app.services.cache_service import (
    get_user_by_id,
    cache_user,
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    # Decode JWT
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    cached_user = get_user_by_id(user_id)

    if cached_user:
        return User(
            id=cached_user["id"],
            role=cached_user["role"],
            name=cached_user["name"],
            email=cached_user["email"],
            password=cached_user["password"],
            created_at=datetime.fromisoformat(
                cached_user["created_at"]
            ),
            updated_at=datetime.fromisoformat(
                cached_user["updated_at"]
            ),
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    cache_user(user)

    return user


def get_current_org_id(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> int:

    organization_user = (
        db.query(OrganizationUser)
        .filter(
            OrganizationUser.user_id == current_user.id
        )
        .first()
    )

    if not organization_user:
        raise HTTPException(
            status_code=403,
            detail="User is not associated with any organization",
        )

    return organization_user.org_id