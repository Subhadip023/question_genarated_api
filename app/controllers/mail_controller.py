"""Mail Controller — acts as Controller (C) in MVC architecture."""

from app.schemas.mail_schema import MailSendRequest, MailSendResponse
from app.services.mail_service import MailService, MailServiceError


class MailControllerError(Exception):
    """Exception for mail controller errors."""
    pass


class MailController:
    @staticmethod
    def send(request_data: MailSendRequest) -> MailSendResponse:
        """Process mail sending request and return standardized response."""
        try:
            result = MailService.send_mail(
                to_email=request_data.to_email,
                subject=request_data.subject,
                body=request_data.body,
            )
            return MailSendResponse(**result)
        except MailServiceError as exc:
            raise MailControllerError(str(exc)) from exc
