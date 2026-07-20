"""
Mail sending API routes — POST /mail/send and POST /send-mail endpoints.
"""

from fastapi import APIRouter, HTTPException

from app.controllers.mail_controller import MailController, MailControllerError
from app.schemas.mail_schema import MailSendRequest, MailSendResponse

router = APIRouter(tags=["Mail / Email"])


@router.post("/mail/send", response_model=MailSendResponse, status_code=200)
@router.post("/send-mail", response_model=MailSendResponse, status_code=200)
def send_email(request_data: MailSendRequest) -> MailSendResponse:
    """
    Send an email via POST request.

    Accepts JSON body:
    - **to_email** (or `email` / `to`): Recipient email address (e.g., "user@example.com")
    - **subject**: Email subject text
    - **body** (or `message` / `content`): Email body content (HTML or plain text)
    """
    try:
        return MailController.send(request_data)
    except MailControllerError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
