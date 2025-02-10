import logging

logger = logging.getLogger(__name__)


class AsyncEmailSender:
    def send_email(self, user_id: str, subject: str, body: str):
        logger.info(
            f"Sending email to {user_id} with subject {subject} and body {body}"
        )
