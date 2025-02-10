import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Annotated, Generic, Optional, TypeVar, Union

import prisma
from prisma import Json
from prisma.enums import NotificationType
from prisma.models import NotificationEvent, UserNotificationBatch
from prisma.types import UserNotificationBatchWhereInput

# from backend.notifications.models import NotificationEvent
from pydantic import BaseModel, EmailStr, Field, field_validator

logger = logging.getLogger(__name__)


T_co = TypeVar("T_co", bound="BaseNotificationData", covariant=True)


class BatchingStrategy(str, Enum):
    IMMEDIATE = "immediate"  # Send right away (errors, critical notifications)
    HOURLY = "hourly"  # Batch for up to an hour (usage reports)
    DAILY = "daily"  # Daily digest (summary notifications)
    BACKOFF = "backoff"  # Backoff strategy (exponential backoff)


class BaseNotificationData(BaseModel):
    pass


class AgentRunData(BaseNotificationData):
    agent_name: str
    credits_used: float
    # remaining_balance: float
    execution_time: float
    graph_id: str
    node_count: int = Field(..., description="Number of nodes executed")


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
            NotificationType.AGENT_RUN: BatchingStrategy.HOURLY,
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


class NotificationPreference(BaseModel):
    user_id: str
    email: EmailStr
    preferences: dict[NotificationType, bool] = {}  # Which notifications they want
    daily_limit: int = 10  # Max emails per day
    emails_sent_today: int = 0
    last_reset_date: datetime = datetime.now()


def get_batch_delay(notification_type: NotificationType) -> timedelta:
    return {
        NotificationType.AGENT_RUN: timedelta(minutes=1),
        NotificationType.ZERO_BALANCE: timedelta(minutes=60),
        NotificationType.LOW_BALANCE: timedelta(minutes=60),
        NotificationType.BLOCK_EXECUTION_FAILED: timedelta(minutes=60),
        NotificationType.CONTINUOUS_AGENT_ERROR: timedelta(minutes=60),
    }[notification_type]


async def create_or_add_to_user_notification_batch(
    user_id: str,
    notification_type: NotificationType,
    data: NotificationEventModel[T_co],
) -> UserNotificationBatch:

    notification_data = Json(data.model_dump(exclude={"user_id", "type", "created_at"}))

    upsert = await UserNotificationBatch.prisma().upsert(
        where=UserNotificationBatchWhereInput(userId=user_id, type=notification_type),
        data={
            "create": {
                "userId": user_id,
                "type": notification_type,
                "notifications": {
                    "create": [{"type": notification_type, "data": notification_data}]
                },
            },
            "update": {
                "notifications": {
                    "create": [{"type": notification_type, "data": notification_data}]
                },
            },
        },
        include={"notifications": True},
    )
    return upsert


async def get_user_notification_last_message_in_batch(
    user_id: str,
    notification_type: NotificationType,
) -> NotificationEvent | None:
    batch = await UserNotificationBatch.prisma().find_first(
        where={"userId": user_id, "type": notification_type},
        order={"createdAt": "desc"},
    )
    if not batch:
        return None
    if not batch.notifications:
        return None
    return batch.notifications[-1]


async def empty_user_notification_batch(
    user_id: str, notification_type: NotificationType
) -> None:
    async with prisma.Prisma().tx() as transaction:
        await transaction.notificationevent.delete_many(
            where={
                "UserNotificationBatch": {
                    "is": {"userId": user_id, "type": notification_type}
                }
            }
        )

        await transaction.usernotificationbatch.delete_many(
            where=UserNotificationBatchWhereInput(
                userId=user_id,
                type=notification_type,
            )
        )
