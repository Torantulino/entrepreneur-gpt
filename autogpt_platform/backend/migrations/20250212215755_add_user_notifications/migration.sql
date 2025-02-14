-- CreateEnum
CREATE TYPE "NotificationType" AS ENUM ('AGENT_RUN', 'ZERO_BALANCE', 'LOW_BALANCE', 'BLOCK_EXECUTION_FAILED', 'CONTINUOUS_AGENT_ERROR', 'DAILY_SUMMARY', 'WEEKLY_SUMMARY', 'MONTHLY_SUMMARY');

-- AlterTable
ALTER TABLE "User" ADD COLUMN     "maxEmailsPerDay" INTEGER NOT NULL DEFAULT 3,
ADD COLUMN     "notifyOnAgentRun" BOOLEAN NOT NULL DEFAULT true,
ADD COLUMN     "notifyOnBlockExecutionFailed" BOOLEAN NOT NULL DEFAULT true,
ADD COLUMN     "notifyOnContinuousAgentError" BOOLEAN NOT NULL DEFAULT true,
ADD COLUMN     "notifyOnDailySummary" BOOLEAN NOT NULL DEFAULT true,
ADD COLUMN     "notifyOnLowBalance" BOOLEAN NOT NULL DEFAULT true,
ADD COLUMN     "notifyOnMonthlySummary" BOOLEAN NOT NULL DEFAULT true,
ADD COLUMN     "notifyOnWeeklySummary" BOOLEAN NOT NULL DEFAULT true,
ADD COLUMN     "notifyOnZeroBalance" BOOLEAN NOT NULL DEFAULT true;

-- CreateTable
CREATE TABLE "NotificationEvent" (
    "id" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "userNotificationBatchId" TEXT,
    "type" "NotificationType" NOT NULL,
    "data" JSONB NOT NULL,

    CONSTRAINT "NotificationEvent_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "UserNotificationBatch" (
    "id" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "userId" TEXT NOT NULL,
    "type" "NotificationType" NOT NULL,

    CONSTRAINT "UserNotificationBatch_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "UserNotificationBatch_userId_type_key" ON "UserNotificationBatch"("userId", "type");

-- AddForeignKey
ALTER TABLE "NotificationEvent" ADD CONSTRAINT "NotificationEvent_userNotificationBatchId_fkey" FOREIGN KEY ("userNotificationBatchId") REFERENCES "UserNotificationBatch"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "UserNotificationBatch" ADD CONSTRAINT "UserNotificationBatch_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
