"""Application services package."""

from app.services.mail_service import MailService, MailServiceError, send_email

__all__ = ["MailService", "MailServiceError", "send_email"]
