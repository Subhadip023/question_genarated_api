"""
Mail Service — handles sending emails using SMTP (smtplib).
Provides a global `send_email` utility function usable everywhere in the backend.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)


class MailServiceError(Exception):
    """Exception raised when email sending fails."""
    pass


def send_email(
    to_email: str,
    subject: str,
    body: str,
    sender_email: str | None = None,
    fail_silently: bool = False,
) -> dict:
    """
    Global utility function to send emails from anywhere in the application.

    Usage:
        from app.services.mail_service import send_email

        send_email(
            to_email="user@example.com",
            subject="Hello",
            body="<h1>Welcome to QMaster</h1>"
        )
    """
    if not to_email or not to_email.strip():
        if fail_silently:
            logger.warning("Recipient email (to_email) is empty; skipping mail send.")
            return {"status": "skipped", "message": "Recipient email address was empty"}
        raise MailServiceError("Recipient email address (to_email) cannot be empty.")

    if not body or not body.strip():
        if fail_silently:
            logger.warning("Email body is empty; skipping mail send.")
            return {"status": "skipped", "message": "Email body was empty"}
        raise MailServiceError("Email body cannot be empty.")

    from_email = (
        sender_email
        or settings.smtp_from_email
        or settings.smtp_user
        or "noreply@questionmaster.com"
    )

    # Construct email message
    msg = MIMEMultipart("alternative")
    msg["From"] = from_email
    msg["To"] = to_email.strip()
    msg["Subject"] = subject.strip() if subject else "Notification"

    # Determine content type (HTML vs Plain Text)
    content_type = "html" if ("<" in body and ">" in body) else "plain"
    msg.attach(MIMEText(body, content_type, "utf-8"))

    # Check if SMTP server is configured
    if settings.smtp_user and settings.smtp_password:
        try:
            logger.info(
                f"Connecting to SMTP server {settings.smtp_host}:{settings.smtp_port} to send mail to {to_email}..."
            )
            if settings.smtp_port == 465 or settings.smtp_use_ssl:
                with smtplib.SMTP_SSL(
                    settings.smtp_host, settings.smtp_port, timeout=15
                ) as server:
                    server.login(settings.smtp_user, settings.smtp_password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(
                    settings.smtp_host, settings.smtp_port, timeout=15
                ) as server:
                    if settings.smtp_use_tls:
                        server.starttls()
                    server.login(settings.smtp_user, settings.smtp_password)
                    server.send_message(msg)
            logger.info(f"Email successfully delivered to {to_email} via SMTP.")
            return {
                "status": "success",
                "message": f"Email successfully delivered to {to_email}",
                "to_email": to_email,
                "subject": subject,
            }
        except Exception as exc:
            logger.error(f"Failed to send email to {to_email} via SMTP ({exc}).")
            if fail_silently:
                return {
                    "status": "error",
                    "message": f"SMTP error: {exc}",
                    "to_email": to_email,
                    "subject": subject,
                }
            raise MailServiceError(f"SMTP error: {exc}") from exc
    else:
        # Development / Fallback mode when SMTP credentials are missing
        logger.info(
            f"[DEV MAIL LOG] Simulated email dispatch:\n"
            f"From: {from_email}\n"
            f"To: {to_email}\n"
            f"Subject: {subject}\n"
            f"Body: {body[:300]}..."
        )

    return {
        "status": "success",
        "message": f"Simulated email logged to server console for {to_email}",
        "to_email": to_email,
        "subject": subject,
    }


class MailService:
    """Class wrapper for MailService operations."""

    @staticmethod
    def send_mail(
        to_email: str,
        subject: str,
        body: str,
        sender_email: str | None = None,
        fail_silently: bool = False,
    ) -> dict:
        """Alias method matching controller usage."""
        return send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            sender_email=sender_email,
            fail_silently=fail_silently,
        )
