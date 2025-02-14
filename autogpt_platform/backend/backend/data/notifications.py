import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Annotated, Any, Generic, Optional, TypeVar, Union

from prisma import Json
from prisma.enums import NotificationType
from prisma.models import NotificationEvent, UserNotificationBatch
from prisma.types import UserNotificationBatchWhereInput

# from backend.notifications.models import NotificationEvent
from pydantic import BaseModel, EmailStr, Field, field_validator

from backend.server.v2.store.exceptions import DatabaseError

from .db import transaction

logger = logging.getLogger(__name__)


T_co = TypeVar("T_co", bound="BaseNotificationData", covariant=True)


class BatchingStrategy(Enum):
    IMMEDIATE = "immediate"  # Send right away (errors, critical notifications)
    HOURLY = "hourly"  # Batch for up to an hour (usage reports)
    DAILY = "daily"  # Daily digest (summary notifications)
    BACKOFF = "backoff"  # Backoff strategy (exponential backoff)


class BaseNotificationData(BaseModel):
    pass


class AgentRunData(BaseNotificationData):
    agent_name: str
    credits_used: float
    execution_time: float
    node_count: int = Field(..., description="Number of nodes executed")
    graph_id: str
    outputs: dict[str, Any] = Field(..., description="Outputs of the agent")


class ZeroBalanceData(BaseNotificationData):
    last_transaction: float
    last_transaction_time: datetime
    top_up_link: str


class LowBalanceData(BaseNotificationData):
    current_balance: float
    threshold_amount: float
    top_up_link: str
    recent_usage: float = Field(..., description="Usage in the last 24 hours")


class BlockExecutionFailedData(BaseNotificationData):
    block_name: str
    block_id: str
    error_message: str
    graph_id: str
    node_id: str
    execution_id: str


class ContinuousAgentErrorData(BaseNotificationData):
    agent_name: str
    error_message: str
    graph_id: str
    execution_id: str
    start_time: datetime
    error_time: datetime
    attempts: int = Field(..., description="Number of retry attempts made")


class BaseSummaryData(BaseNotificationData):
    total_credits_used: float
    total_executions: int
    most_used_agent: str
    total_execution_time: float
    successful_runs: int
    failed_runs: int
    average_execution_time: float
    cost_breakdown: dict[str, float]


class DailySummaryData(BaseSummaryData):
    date: datetime


class WeeklySummaryData(BaseSummaryData):
    start_date: datetime
    end_date: datetime
    week_number: int
    year: int


class MonthlySummaryData(BaseSummaryData):
    month: int
    year: int


NotificationData = Annotated[
    Union[
        AgentRunData,
        ZeroBalanceData,
        LowBalanceData,
        BlockExecutionFailedData,
        ContinuousAgentErrorData,
        MonthlySummaryData,
    ],
    Field(discriminator="type"),
]


class NotificationEventDTO(BaseModel):
    user_id: str
    type: NotificationType
    data: dict
    created_at: datetime = Field(default_factory=datetime.now)


class NotificationEventModel(BaseModel, Generic[T_co]):
    user_id: str
    type: NotificationType
    data: T_co
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def strategy(self) -> BatchingStrategy:
        return NotificationTypeOverride(self.type).strategy

    @field_validator("type", mode="before")
    def uppercase_type(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v

    @property
    def template(self) -> str:
        return NotificationTypeOverride(self.type).template


def get_data_type(
    notification_type: NotificationType,
) -> type[BaseNotificationData]:
    return {
        NotificationType.AGENT_RUN: AgentRunData,
        NotificationType.ZERO_BALANCE: ZeroBalanceData,
        NotificationType.LOW_BALANCE: LowBalanceData,
        NotificationType.BLOCK_EXECUTION_FAILED: BlockExecutionFailedData,
        NotificationType.CONTINUOUS_AGENT_ERROR: ContinuousAgentErrorData,
        NotificationType.DAILY_SUMMARY: DailySummaryData,
        NotificationType.WEEKLY_SUMMARY: WeeklySummaryData,
        NotificationType.MONTHLY_SUMMARY: MonthlySummaryData,
    }[notification_type]


class NotificationBatch(BaseModel):
    user_id: str
    events: list[NotificationEvent]
    strategy: BatchingStrategy
    last_update: datetime = datetime.now()


class NotificationResult(BaseModel):
    success: bool
    message: Optional[str] = None


class NotificationTypeOverride:
    def __init__(self, notification_type: NotificationType):
        self.notification_type = notification_type

    @property
    def strategy(self) -> BatchingStrategy:
        BATCHING_RULES = {
            # These are batched by the notification service
            NotificationType.AGENT_RUN: BatchingStrategy.IMMEDIATE,
            # These are batched by the notification service, but with a backoff strategy
            NotificationType.ZERO_BALANCE: BatchingStrategy.BACKOFF,
            NotificationType.LOW_BALANCE: BatchingStrategy.BACKOFF,
            NotificationType.BLOCK_EXECUTION_FAILED: BatchingStrategy.BACKOFF,
            NotificationType.CONTINUOUS_AGENT_ERROR: BatchingStrategy.BACKOFF,
            # These aren't batched by the notification service, so we send them right away
            NotificationType.DAILY_SUMMARY: BatchingStrategy.IMMEDIATE,
            NotificationType.WEEKLY_SUMMARY: BatchingStrategy.IMMEDIATE,
            NotificationType.MONTHLY_SUMMARY: BatchingStrategy.IMMEDIATE,
        }
        return BATCHING_RULES.get(self.notification_type, BatchingStrategy.HOURLY)

    @property
    def template(self) -> str:
        """Returns template name for this notification type"""
        return {
            NotificationType.AGENT_RUN: "agent_run.html",
            NotificationType.ZERO_BALANCE: "zero_balance.html",
            NotificationType.LOW_BALANCE: "low_balance.html",
            NotificationType.BLOCK_EXECUTION_FAILED: "block_failed.html",
            NotificationType.CONTINUOUS_AGENT_ERROR: "agent_error.html",
            NotificationType.DAILY_SUMMARY: "daily_summary.html",
            NotificationType.WEEKLY_SUMMARY: "weekly_summary.html",
            NotificationType.MONTHLY_SUMMARY: "monthly_summary.html",
        }[self.notification_type]

    @property
    def subject(self) -> str:
        return {
            NotificationType.AGENT_RUN: "Agent Run Report",
            NotificationType.ZERO_BALANCE: "You're out of credits!",
            NotificationType.LOW_BALANCE: "Low Balance Warning!",
            NotificationType.BLOCK_EXECUTION_FAILED: "Uh oh! Block Execution Failed",
            NotificationType.CONTINUOUS_AGENT_ERROR: "Shoot! Continuous Agent Error",
            NotificationType.DAILY_SUMMARY: "Here's your daily summary!",
            NotificationType.WEEKLY_SUMMARY: "Look at all the cool stuff you did last week!",
            NotificationType.MONTHLY_SUMMARY: "We did a lot this month!",
        }[self.notification_type]


class NotificationPreferenceDTO(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    preferences: dict[NotificationType, bool] = Field(
        ..., description="Which notifications the user wants"
    )
    daily_limit: int = Field(..., description="Max emails per day")


class NotificationPreference(BaseModel):
    user_id: str
    email: EmailStr
    preferences: dict[NotificationType, bool] = Field(
        default_factory=dict, description="Which notifications the user wants"
    )
    daily_limit: int = 10  # Max emails per day
    emails_sent_today: int = 0
    last_reset_date: datetime = Field(default_factory=datetime.now)


def get_batch_delay(notification_type: NotificationType) -> timedelta:
    return {
        NotificationType.AGENT_RUN: timedelta(seconds=1),
        NotificationType.ZERO_BALANCE: timedelta(minutes=60),
        NotificationType.LOW_BALANCE: timedelta(minutes=60),
        NotificationType.BLOCK_EXECUTION_FAILED: timedelta(minutes=60),
        NotificationType.CONTINUOUS_AGENT_ERROR: timedelta(minutes=60),
    }[notification_type]


async def create_or_add_to_user_notification_batch(
    user_id: str,
    notification_type: NotificationType,
    data: str,  # type: 'NotificationEventModel'
) -> dict:
    try:
        logger.info(
            f"Creating or adding to notification batch for {user_id} with type {notification_type} and data {data}"
        )

        notification_data = NotificationEventModel[
            get_data_type(notification_type)
        ].model_validate_json(data)

        # Serialize the data
        json_data: Json = Json(notification_data.data.model_dump_json())

        # First try to find existing batch
        existing_batch = await UserNotificationBatch.prisma().find_unique(
            where={
                "userId_type": {
                    "userId": user_id,
                    "type": notification_type,
                }
            },
            include={"notifications": True},
        )

        if not existing_batch:
            async with transaction() as tx:
                notification_event = await tx.notificationevent.create(
                    data={
                        "type": notification_type,
                        "data": json_data,
                    }
                )

                # Create new batch
                resp = await tx.usernotificationbatch.create(
                    data={
                        "userId": user_id,
                        "type": notification_type,
                        "notifications": {"connect": [{"id": notification_event.id}]},
                    },
                    include={"notifications": True},
                )
                return resp.model_dump()
        else:
            async with transaction() as tx:
                notification_event = await tx.notificationevent.create(
                    data={
                        "type": notification_type,
                        "data": json_data,
                        "UserNotificationBatch": {"connect": {"id": existing_batch.id}},
                    }
                )
                # Add to existing batch
                resp = await tx.usernotificationbatch.update(
                    where={"id": existing_batch.id},
                    data={
                        "notifications": {"connect": [{"id": notification_event.id}]}
                    },
                    include={"notifications": True},
                )
            if not resp:
                raise DatabaseError(
                    f"Failed to add notification event {notification_event.id} to existing batch {existing_batch.id}"
                )
            return resp.model_dump()
    except Exception as e:
        raise DatabaseError(
            f"Failed to create or add to notification batch for user {user_id} and type {notification_type}: {e}"
        ) from e


async def get_user_notification_last_message_in_batch(
    user_id: str,
    notification_type: NotificationType,
) -> NotificationEvent | None:
    try:
        batch = await UserNotificationBatch.prisma().find_first(
            where={"userId": user_id, "type": notification_type},
            order={"createdAt": "desc"},
        )
        if not batch:
            return None
        if not batch.notifications:
            return None
        return batch.notifications[-1]
    except Exception as e:
        raise DatabaseError(
            f"Failed to get user notification last message in batch for user {user_id} and type {notification_type}: {e}"
        ) from e


async def empty_user_notification_batch(
    user_id: str, notification_type: NotificationType
) -> None:
    try:
        async with transaction() as tx:
            await tx.notificationevent.delete_many(
                where={
                    "UserNotificationBatch": {
                        "is": {"userId": user_id, "type": notification_type}
                    }
                }
            )

            await tx.usernotificationbatch.delete_many(
                where=UserNotificationBatchWhereInput(
                    userId=user_id,
                    type=notification_type,
                )
            )
    except Exception as e:
        raise DatabaseError(
            f"Failed to empty user notification batch for user {user_id} and type {notification_type}: {e}"
        ) from e


async def get_user_notification_batch(
    user_id: str,
    notification_type: NotificationType,
) -> UserNotificationBatch | None:
    try:
        return await UserNotificationBatch.prisma().find_first(
            where={"userId": user_id, "type": notification_type},
            include={"notifications": True},
        )
    except Exception as e:
        raise DatabaseError(
            f"Failed to get user notification batch for user {user_id} and type {notification_type}: {e}"
        ) from e
