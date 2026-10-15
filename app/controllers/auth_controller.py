"""Authentication controller."""

from datetime import datetime, timedelta, timezone
import logging
import secrets
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.organization import Organization
from app.models.organization_user import OrganizationUser
from app.models.user import User
from app.models.password_reset_otp import PasswordResetOTP
from app.schemas.user import (
    ForgotPasswordResetRequest,
    ForgotPasswordResponse,
    LoginRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    StudentRegister,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import create_access_token, hash_password, verify_password
from app.services.cache_service import (
    cache_user,
    get_user_by_email,
    delete_user_cache,
)
from app.services.mail_service import send_email, MailServiceError

logger = logging.getLogger(__name__)


class InvalidCredentialsError(Exception):
    """Raised when login credentials are incorrect."""


class AccountDeactivatedError(Exception):
    """Raised when an organization account is deactivated."""


class EmailAlreadyExistsError(Exception):
    """Raised when a registration email is already used."""


class InvalidOldPasswordError(Exception):
    """Raised when the supplied current password is incorrect."""


class PasswordConfirmationError(Exception):
    """Raised when the new password and its confirmation differ."""


class InvalidOTPError(Exception):
    """Raised when the provided OTP is invalid or not found."""


class ExpiredOTPError(Exception):
    """Raised when the provided OTP has expired."""


class PasswordTooShortError(Exception):
    """Raised when the new password is too short."""


class AuthController:
    @staticmethod
    def register_student(
        data: StudentRegister,
        db: Session
    ) -> UserResponse:

        student = User(
            role=3,
            name=data.name.strip(),
            email=data.email.strip().lower(),
            password=hash_password(data.password),
        )

        try:
            db.add(student)
            db.commit()
            db.refresh(student)

            # Store in Redis
            cache_user(student)

        except IntegrityError as exc:
            db.rollback()
            raise EmailAlreadyExistsError from exc

        return UserResponse.model_validate(student)

    @staticmethod
    def login(data: LoginRequest, db: Session) -> TokenResponse:
        email = data.email.strip().lower()

        cached_user = get_user_by_email(email)

        if cached_user:
            print(f"REDIS HIT: {email}")
            # Redis HIT
            user_id = cached_user["id"]
            user_role = cached_user["role"]
            user_name = cached_user["name"]
            user_email = cached_user["email"]
            user_password = cached_user["password"]
            created_at = datetime.fromisoformat(
                cached_user["created_at"]
            )
            updated_at = datetime.fromisoformat(
                cached_user["updated_at"]
            )

        else:
            print(f"REDIS MISS: {email}")
            # Redis MISS -> Get user from MySQL
            user = (
                db.query(User)
                .filter(User.email == email)
                .first()
            )

            if user is None:
                raise InvalidCredentialsError

            # Store user in Redis
            cache_user(user)

            user_id = user.id
            user_role = user.role
            user_name = user.name
            user_email = user.email
            user_password = user.password
            created_at = user.created_at
            updated_at = user.updated_at

        # Verify password
        if not verify_password(data.password, user_password):
            raise InvalidCredentialsError

        # Organization check
        if user_role == 0:
            organization_id = 0
            organization_name = "Global"

        else:
            organization = (
                db.query(Organization)
                .join(
                    OrganizationUser,
                    OrganizationUser.org_id == Organization.id
                )
                .filter(
                    OrganizationUser.user_id == user_id
                )
                .order_by(Organization.id)
                .first()
            )

            if organization and not organization.is_active:
                raise AccountDeactivatedError(
                    "Account is not active, Contact to super admin"
                )

            organization_id = (
                organization.id
                if organization
                else None
            )

            organization_name = (
                organization.name
                if organization
                else None
            )

        token, expires_in = create_access_token(
            user_id,
            user_role
        )

        user_response = UserResponse(
            id=user_id,
            role=user_role,
            name=user_name,
            email=user_email,
            created_at=created_at,
            updated_at=updated_at,
        )

        return TokenResponse(
            message=f"Welcome, {user_name}!",
            access_token=token,
            expires_in=expires_in,
            organization_id=organization_id,
            organization_name=organization_name,
            user_role=user_role,
            user=user_response,
        )

    @staticmethod
    def reset_password(
        user_id: int,
        data: ResetPasswordRequest,
        db: Session
    ) -> ResetPasswordResponse:

        if data.new_password != data.confirm_new_password:
            raise PasswordConfirmationError

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None or not verify_password(
            data.old_password,
            user.password
        ):
            raise InvalidOldPasswordError

        user.password = hash_password(
            data.new_password
        )

        try:
            db.commit()
            db.refresh(user)

            # Update Redis
            cache_user(user)

        except Exception:
            db.rollback()
            raise

        return ResetPasswordResponse()

    @staticmethod
    def send_forgot_password_otp(
        email: str,
        db: Session,
    ) -> ForgotPasswordResponse:
        clean_email = email.strip().lower()
        user = db.query(User).filter(User.email == clean_email).first()

        # If user is not found, return generic success to avoid email enumeration
        if not user:
            return ForgotPasswordResponse(
                message="If this email is registered, a password reset code has been sent."
            )

        # Invalidate any previously active OTPs for this email
        db.query(PasswordResetOTP).filter(
            PasswordResetOTP.email == clean_email,
            PasswordResetOTP.is_used == False,
        ).update({"is_used": True})

        # Generate a secure 6-digit numeric OTP
        otp_code = f"{secrets.randbelow(900000) + 100000}"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        otp_record = PasswordResetOTP(
            email=clean_email,
            otp_code=otp_code,
            expires_at=expires_at,
            is_used=False,
        )
        db.add(otp_record)
        db.commit()

        # Construct styled HTML email
        subject = f"{otp_code} is your Safalya password reset code"
        body_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 520px; margin: 0 auto; padding: 32px 24px; border: 1px solid #e2e8f0; border-radius: 12px; background-color: #ffffff; color: #1e293b;">
            <div style="text-align: center; margin-bottom: 24px;">
                <h1 style="color: #0f172a; margin: 0; font-size: 24px; font-weight: 700;">Password Reset Request</h1>
                <p style="color: #64748b; font-size: 14px; margin-top: 6px;">Safalya · The Smart Assessment Platform</p>
            </div>
            <p style="font-size: 15px; line-height: 1.6; margin-bottom: 16px;">Hello <strong>{user.name}</strong>,</p>
            <p style="font-size: 15px; line-height: 1.6; margin-bottom: 24px;">We received a request to reset the password for your account. Use the verification code below to proceed:</p>
            <div style="text-align: center; margin: 28px 0;">
                <span style="display: inline-block; font-size: 36px; font-weight: 800; letter-spacing: 10px; color: #4f46e5; background-color: #f5f3ff; padding: 16px 28px; border-radius: 10px; border: 2px dashed #c7d2fe;">{otp_code}</span>
            </div>
            <p style="font-size: 13px; color: #64748b; line-height: 1.5; margin-bottom: 8px;">⏱️ This code is valid for <strong>10 minutes</strong> only.</p>
            <p style="font-size: 13px; color: #94a3b8; line-height: 1.5;">If you did not request this, please ignore this email. Your account remains completely secure.</p>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;" />
            <p style="color: #94a3b8; font-size: 12px; text-align: center; margin: 0;">© Safalya Assessment Platform. All rights reserved.</p>
        </div>
        """

        try:
            send_email(
                to_email=clean_email,
                subject=subject,
                body=body_html,
            )
        except Exception as exc:
            logger.error(f"Failed to send OTP email to {clean_email}: {exc}")
            raise MailServiceError("Unable to deliver password reset email. Please try again.") from exc

        return ForgotPasswordResponse(
            message="If this email is registered, a password reset code has been sent."
        )

    @staticmethod
    def reset_password_with_otp(
        data: ForgotPasswordResetRequest,
        db: Session,
    ) -> ForgotPasswordResponse:
        clean_email = data.email.strip().lower()
        clean_otp = data.otp.strip()

        if data.new_password != data.confirm_new_password:
            raise PasswordConfirmationError("New password and confirmation do not match")

        if len(data.new_password) < 8:
            raise PasswordTooShortError("Password must be at least 8 characters long")

        user = db.query(User).filter(User.email == clean_email).first()
        if not user:
            raise InvalidOTPError("Invalid email or verification code")

        now = datetime.now(timezone.utc)
        otp_entry = (
            db.query(PasswordResetOTP)
            .filter(
                PasswordResetOTP.email == clean_email,
                PasswordResetOTP.otp_code == clean_otp,
                PasswordResetOTP.is_used == False,
            )
            .order_by(PasswordResetOTP.created_at.desc())
            .first()
        )

        if not otp_entry:
            raise InvalidOTPError("Invalid or already used verification code")

        expires_at = otp_entry.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < now:
            raise ExpiredOTPError("Verification code has expired. Please request a new code.")

        # Update password
        user.password = hash_password(data.new_password)
        otp_entry.is_used = True

        try:
            db.commit()
            db.refresh(user)
            cache_user(user)
        except Exception:
            db.rollback()
            raise

        return ForgotPasswordResponse(
            message="Your password has been successfully reset. You can now sign in."
        )

