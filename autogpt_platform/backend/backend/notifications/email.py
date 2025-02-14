import logging
import pathlib

from postmarker.core import PostmarkClient
from postmarker.models.emails import EmailManager
from prisma.enums import NotificationType
from pydantic import BaseModel

from backend.data.notifications import (
    NotificationEventModel,
    NotificationTypeOverride,
    T_co,
)
from backend.util.settings import Settings
from backend.util.text import TextFormatter

logger = logging.getLogger(__name__)
settings = Settings()


# The following is a workaround to get the type checker to recognize the EmailManager type
# This is a temporary solution and should be removed once the Postmark library is updated
# to support type annotations.
class TypedPostmarkClient(PostmarkClient):
    emails: EmailManager


class Template(BaseModel):
    subject: str
    body: str
    base_template: str


class EmailSender:
    def __init__(self):
        if settings.secrets.postmark_server_api_token:
            self.postmark = TypedPostmarkClient(
                server_token=settings.secrets.postmark_server_api_token
            )
        else:
            logger.warning(
                "Postmark server API token not found, email sending disabled"
            )
        self.formatter = TextFormatter()

    def send_templated(
        self,
        notification: NotificationType,
        user_email: str,
        data: NotificationEventModel[T_co] | list[NotificationEventModel[T_co]],
    ):
        """Send an email to a user using a template pulled from the notification type"""
        if not self.postmark:
            logger.warning("Postmark client not initialized, email not sent")
            return
        template = self._get_template(notification)

        try:
            subject, full_message = self.formatter.format_email(
                base_template=template.base_template,
                subject_template=template.subject,
                content_template=template.body,
                data=data,
                unsubscribe_link="https://autogpt.com/unsubscribe",
            )

        except Exception as e:
            logger.error(f"Error formatting full message: {e}")
            raise e

        self._send_email(user_email, subject, full_message)

    def _get_template(self, notification: NotificationType):
        # convert the notification type to a notification type override
        notification_type_override = NotificationTypeOverride(notification)
        # find the template in templates/name.html (the .template returns with the .html)
        template_path = f"templates/{notification_type_override.template}.jinja2"
        logger.debug(
            f"Template full path: {pathlib.Path(__file__).parent / template_path}"
        )
        base_template_path = "templates/base.html.jinja2"
        with open(pathlib.Path(__file__).parent / base_template_path, "r") as file:
            base_template = file.read()
        with open(pathlib.Path(__file__).parent / template_path, "r") as file:
            template = file.read()
        return Template(
            subject=notification_type_override.subject,
            body=template,
            base_template=base_template,
        )

    def _send_email(self, user_email: str, subject: str, body: str):
        logger.debug(f"Sending email to {user_email} with subject {subject}")
        self.postmark.emails.send(
            From=settings.config.postmark_sender_email,
            To=user_email,
            Subject=subject,
            HtmlBody=body,
        )
