"""Mail Pydantic schemas for mail send requests and responses."""

from typing import Any
from pydantic import BaseModel, Field, model_validator


class MailSendRequest(BaseModel):
    """
    Request model for sending email.
    Supports flexible key names: to_email / email / to, and body / message / content.
    """
    to_email: str = Field(..., description="Recipient email address", example="user@example.com")
    subject: str = Field(default="Message from Question Generator API", description="Email subject")
    body: str = Field(..., description="Email body content (supports HTML or plain text)")

    @model_validator(mode="before")
    @classmethod
    def populate_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Recipient email aliases: to_email, email, to
            if "to_email" not in data:
                if "email" in data:
                    data["to_email"] = data["email"]
                elif "to" in data:
                    data["to_email"] = data["to"]

            # Body content aliases: body, message, content
            if "body" not in data:
                if "message" in data:
                    data["body"] = data["message"]
                elif "content" in data:
                    data["body"] = data["content"]
        return data


class MailSendResponse(BaseModel):
    """Response model for email sending operation."""
    status: str = "success"
    message: str = "Email sent successfully"
    to_email: str
    subject: str
