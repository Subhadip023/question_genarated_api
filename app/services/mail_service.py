"""
Mail Service — handles sending emails using SMTP (smtplib).
Falls back to logging mail content in development when SMTP is unconfigured.
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


class MailService:
    @staticmethod
    def send_mail(to_email: str, subject: str, body: str) -> dict:
        """
        Sends an email to the specified recipient address with subject and body.
        Supports HTML content formatting if body contains HTML tags.
        """
        if not to_email or not to_email.strip():
            raise MailServiceError("Recipient email address (to_email) cannot be empty.")

        if not body or not body.strip():
            raise MailServiceError("Email body cannot be empty.")

        sender_email = settings.smtp_from_email or settings.smtp_user or "noreply@questionmaster.com"

        # Construct email message
        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        msg["To"] = to_email.strip()
        msg["Subject"] = subject.strip() if subject else "Notification"

        # Determine if content is HTML or Plain text
        content_type = "html" if ("<" in body and ">" in body) else "plain"
        msg.attach(MIMEText(body, content_type, "utf-8"))

        # Check if SMTP server details are configured
        if settings.smtp_user and settings.smtp_password:
            try:
                logger.info(f"Connecting to SMTP server {settings.smtp_host}:{settings.smtp_port} to send mail to {to_email}...")
                if settings.smtp_port == 465 or settings.smtp_use_ssl:
                    with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15) as server:
                        server.login(settings.smtp_user, settings.smtp_password)
                        server.send_message(msg)
                else:
                    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
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
                raise MailServiceError(f"SMTP error: {exc}") from exc
        else:
            # Development/fallback mode when SMTP credentials are not configured in .env
            logger.info(
                f"[DEV MAIL LOG] Simulated email dispatch:\n"
                f"From: {sender_email}\n"
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
