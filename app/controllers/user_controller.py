"""Business logic for user CRUD operations."""

import hashlib
import secrets

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate


class UserEmailExistsError(Exception):
    """Raised when a user email conflicts with an existing row."""


def _hash_password(password: str) -> str:
    """Hash a password with a random salt using PBKDF2-SHA256."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), 600_000
    ).hex()
    return f"pbkdf2_sha256$600000${salt}${digest}"


class UserController:
    """Controller responsible for user CRUD operations."""

    @staticmethod
    def create_user(data: UserCreate, db: Session) -> UserResponse:
        user = User(
            role=data.role,
            name=data.name.strip(),
            email=data.email.strip().lower(),
            password=_hash_password(data.password),
        )
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
        except IntegrityError as exc:
            db.rollback()
            raise UserEmailExistsError from exc
        except Exception:
            db.rollback()
            raise
        return UserResponse.model_validate(user)

    @staticmethod
    def get_all_users(db: Session) -> list[UserResponse]:
        users = db.query(User).order_by(User.id).all()
        return [UserResponse.model_validate(user) for user in users]

    @staticmethod
    def get_user(user_id: int, db: Session) -> UserResponse | None:
        user = db.query(User).filter(User.id == user_id).first()
        return UserResponse.model_validate(user) if user else None

    @staticmethod
    def update_user(
        user_id: int, data: UserUpdate, db: Session
    ) -> UserResponse | None:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return None

        changes = data.model_dump(exclude_unset=True, exclude_none=True)
        if "name" in changes:
            changes["name"] = changes["name"].strip()
        if "email" in changes:
            changes["email"] = changes["email"].strip().lower()
        if "password" in changes:
            changes["password"] = _hash_password(changes["password"])

        for field, value in changes.items():
            setattr(user, field, value)

        try:
            db.commit()
            db.refresh(user)
        except IntegrityError as exc:
            db.rollback()
            raise UserEmailExistsError from exc
        except Exception:
            db.rollback()
            raise
        return UserResponse.model_validate(user)

    @staticmethod
    def delete_user(user_id: int, db: Session) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return False
        try:
            db.delete(user)
            db.commit()
        except Exception:
            db.rollback()
            raise
        return True
