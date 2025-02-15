import logging
import time
from typing import TYPE_CHECKING

from aio_pika.exceptions import QueueEmpty
from autogpt_libs.utils.cache import thread_cached

from backend.data.notifications import (
    BatchingStrategy,
    NotificationEventDTO,
    NotificationEventModel,
    NotificationResult,
    get_data_type,
)
from backend.data.rabbitmq import Exchange, ExchangeType, Queue, RabbitMQConfig
from backend.executor.database import DatabaseManager
from backend.notifications.email import EmailSender
from backend.util.service import AppService, expose, get_service_client
from backend.util.settings import Settings

if TYPE_CHECKING:
    from backend.executor import DatabaseManager

logger = logging.getLogger(__name__)
settings = Settings()


def create_notification_config() -> RabbitMQConfig:
    """Create RabbitMQ configuration for notifications"""
    notification_exchange = Exchange(name="notifications", type=ExchangeType.TOPIC)

    summary_exchange = Exchange(name="summaries", type=ExchangeType.TOPIC)

    dead_letter_exchange = Exchange(name="dead_letter", type=ExchangeType.DIRECT)
    delay_exchange = Exchange(name="delay", type=ExchangeType.DIRECT)

    queues = [
        # Main notification queues
        Queue(
            name="immediate_notifications",
            exchange=notification_exchange,
            routing_key="notification.immediate.#",
            arguments={
                "x-dead-letter-exchange": dead_letter_exchange.name,
                "x-dead-letter-routing-key": "failed.immediate",
            },
        ),
        Queue(
            name="backoff_notifications",
            exchange=notification_exchange,
            routing_key="notification.backoff.#",
            arguments={
                "x-dead-letter-exchange": dead_letter_exchange.name,
                "x-dead-letter-routing-key": "failed.backoff",
            },
        ),
        # Summary queues
        Queue(
            name="daily_summary_trigger",
            exchange=summary_exchange,
            routing_key="summary.daily",
            arguments={"x-message-ttl": 86400000},  # 24 hours
        ),
        Queue(
            name="weekly_summary_trigger",
            exchange=summary_exchange,
            routing_key="summary.weekly",
            arguments={"x-message-ttl": 604800000},  # 7 days
        ),
        Queue(
            name="monthly_summary_trigger",
            exchange=summary_exchange,
            routing_key="summary.monthly",
            arguments={"x-message-ttl": 2592000000},  # 30 days
        ),
        # Failed notifications queue
        Queue(
            name="failed_notifications",
            exchange=dead_letter_exchange,
            routing_key="failed.#",
        ),
    ]

    return RabbitMQConfig(
        exchanges=[
            notification_exchange,
            # batch_exchange,
            summary_exchange,
            dead_letter_exchange,
            delay_exchange,
        ],
        queues=queues,
    )


class NotificationManager(AppService):
    """Service for handling notifications with batching support"""

    def __init__(self):
        super().__init__()
        self.use_db = True
        self.rabbitmq_config = create_notification_config()
        self.running = True
        self.email_sender = EmailSender()

    @classmethod
    def get_port(cls) -> int:
        return settings.config.notification_service_port

    def get_routing_key(self, event: NotificationEventModel) -> str:
        """Get the appropriate routing key for an event"""
        if event.strategy == BatchingStrategy.IMMEDIATE:
            return f"notification.immediate.{event.type.value}"
        elif event.strategy == BatchingStrategy.BACKOFF:
            return f"notification.backoff.{event.type.value}"
        return f"notification.{event.type.value}"

    @expose
    def queue_notification(self, event: NotificationEventDTO) -> NotificationResult:
        """Queue a notification - exposed method for other services to call"""
        try:
            logger.info(f"Recieved Request to queue {event=}")
            # Workaround for not being able to seralize generics over the expose bus
            parsed_event = NotificationEventModel[
                get_data_type(event.type)
            ].model_validate(event.model_dump())
            routing_key = self.get_routing_key(parsed_event)
            message = parsed_event.model_dump_json()

            logger.info(f"Recieved Request to queue {message=}")

            exchange = "notifications"

            # Publish to RabbitMQ
            self.run_and_wait(
                self.rabbit.publish_message(
                    routing_key=routing_key,
                    message=message,
                    exchange=next(
                        ex for ex in self.rabbit_config.exchanges if ex.name == exchange
                    ),
                )
            )

            return NotificationResult(
                success=True,
                message=(f"Notification queued with routing key: {routing_key}"),
            )

        except Exception as e:
            logger.error(f"Error queueing notification: {e}")
            return NotificationResult(success=False, message=str(e))

    async def _process_immediate(self, message: str) -> bool:
        """Process a single notification immediately, returning whether to put into the failed queue"""
        try:
            event = NotificationEventDTO.model_validate_json(message)
            parsed_event = NotificationEventModel[
                get_data_type(event.type)
            ].model_validate_json(message)
            user_email = get_db_client().get_user_email_by_id(event.user_id)
            should_send = (
                get_db_client()
                .get_user_notification_preference(event.user_id)
                .preferences[event.type]
            )
            if not user_email:
                logger.error(f"User email not found for user {event.user_id}")
                return False
            if not should_send:
                logger.debug(
                    f"User {event.user_id} does not want to receive {event.type} notifications"
                )
                return True
            self.email_sender.send_templated(event.type, user_email, parsed_event)
            logger.info(f"Processing notification: {parsed_event}")
            return True
        except Exception as e:
            logger.error(f"Error processing notification: {e}")
            return False

    def run_service(self):
        logger.info(f"[{self.service_name}] Started notification service")

        # Set up queue consumers
        channel = self.run_and_wait(self.rabbit.get_channel())

        immediate_queue = self.run_and_wait(
            channel.get_queue("immediate_notifications")
        )

        while self.running:
            try:
                # Process immediate notifications
                try:
                    message = self.run_and_wait(immediate_queue.get())

                    if message:
                        success = self.run_and_wait(
                            self._process_immediate(message.body.decode())
                        )
                        if success:
                            self.run_and_wait(message.ack())
                        else:
                            self.run_and_wait(message.reject(requeue=True))
                except QueueEmpty:
                    logger.debug("Immediate queue empty")

                time.sleep(0.1)

            except QueueEmpty as e:
                logger.debug(f"Queue empty: {e}")
            except Exception as e:
                logger.error(f"Error in notification service loop: {e}")

    def cleanup(self):
        """Cleanup service resources"""
        self.running = False
        super().cleanup()

    # ------- UTILITIES ------- #


@thread_cached
def get_db_client() -> "DatabaseManager":
    from backend.executor import DatabaseManager

    return get_service_client(DatabaseManager)
