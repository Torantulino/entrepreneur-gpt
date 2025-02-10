# backend/notifications/summary.py
import logging
from collections import defaultdict
from datetime import datetime
from typing import TYPE_CHECKING

from autogpt_libs.utils.cache import thread_cached

if TYPE_CHECKING:
    from backend.executor.database import DatabaseManager

from backend.data.notifications import (
    DailySummaryData,
    MonthlySummaryData,
    NotificationEventModel,
    NotificationType,
    WeeklySummaryData,
)
from backend.util.service import get_service_client

logger = logging.getLogger(__name__)


class SummaryManager:
    """Handles all summary generation and stats collection"""

    def __init__(self):
        self.summary_keys = {
            "daily": "summary:daily:",
            "weekly": "summary:weekly:",
            "monthly": "summary:monthly:",
        }
        self.last_check_keys = {
            "daily": "summary:last_check:daily",
            "weekly": "summary:last_check:weekly",
            "monthly": "summary:last_check:monthly",
        }

    async def collect_stats(
        self, user_id: str, start_time: datetime, end_time: datetime
    ) -> dict:
        """Collect execution statistics for a time period"""
        db = get_db_client()
        executions = db.get_executions_in_timerange(
            user_id=user_id,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
        )

        stats = {
            "total_credits_used": 0,
            "total_executions": len(executions),
            "total_execution_time": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "agent_usage": defaultdict(float),
        }

        # for execution in executions:
        #     stats["total_credits_used"] += execution.credits_used
        #     stats["total_execution_time"] += execution.execution_time
        #     stats[
        #         "successful_runs" if execution.status == "completed" else "failed_runs"
        #     ] += 1
        #     stats["agent_usage"][execution.agent_type] += execution.credits_used

        most_used = (
            max(stats["agent_usage"].items(), key=lambda x: x[1])[0]
            if stats["agent_usage"]
            else "None"
        )

        return {
            "total_credits_used": stats["total_credits_used"],
            "total_executions": stats["total_executions"],
            "most_used_agent": most_used,
            "total_execution_time": stats["total_execution_time"],
            "successful_runs": stats["successful_runs"],
            "failed_runs": stats["failed_runs"],
            "average_execution_time": (
                stats["total_execution_time"] / stats["total_executions"]
                if stats["total_executions"]
                else 0
            ),
            "cost_breakdown": dict(stats["agent_usage"]),
        }

    async def should_generate_summary(self, summary_type: str, redis) -> bool:
        """Check if we should generate a summary based on last check time"""
        last_check_key = self.last_check_keys[summary_type]
        last_check = await redis.get(last_check_key)

        if not last_check:
            return True

        last_check_time = datetime.fromisoformat(last_check)
        now = datetime.now()

        if summary_type == "daily":
            return now.date() != last_check_time.date()
        elif summary_type == "weekly":
            return now.isocalendar()[1] != last_check_time.isocalendar()[1]
        else:  # monthly
            return now.month != last_check_time.month

    async def generate_summary(
        self,
        summary_type: str,
        user_id: str,
        start_time: datetime,
        end_time: datetime,
        notification_manager,
    ) -> bool:
        """Generate and send a summary for a user"""
        try:
            stats = await self.collect_stats(user_id, start_time, end_time)
            if not stats["total_executions"]:
                return False

            if summary_type == "daily":
                data = DailySummaryData(date=start_time, **stats)
                type_ = NotificationType.DAILY_SUMMARY
                notification = NotificationEventModel(
                    user_id=user_id,
                    type=type_,
                    data=data,
                )
            elif summary_type == "weekly":
                data = WeeklySummaryData(
                    start_date=start_time,
                    end_date=end_time,
                    week_number=start_time.isocalendar()[1],
                    year=start_time.year,
                    **stats,
                )
                type_ = NotificationType.WEEKLY_SUMMARY
                notification = NotificationEventModel(
                    user_id=user_id,
                    type=type_,
                    data=data,
                )
            else:
                data = MonthlySummaryData(
                    month=start_time.month, year=start_time.year, **stats
                )
                type_ = NotificationType.MONTHLY_SUMMARY
                notification = NotificationEventModel(
                    user_id=user_id,
                    type=type_,
                    data=data,
                )
            return await notification_manager._process_immediate(notification)

        except Exception as e:
            logger.error(
                f"Error generating {summary_type} summary for user {user_id}: {e}"
            )
            return False


@thread_cached
def get_db_client() -> "DatabaseManager":
    from backend.executor import DatabaseManager

    return get_service_client(DatabaseManager)
