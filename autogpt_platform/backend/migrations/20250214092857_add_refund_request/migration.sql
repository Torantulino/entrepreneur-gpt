-- CreateEnum
CREATE TYPE "CreditRefundRequestStatus" AS ENUM ('PENDING', 'APPROVED', 'REJECTED');

-- CreateTable
CREATE TABLE "CreditRefundRequest" (
    "id" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "userId" TEXT NOT NULL,
    "transactionKey" TEXT NOT NULL,
    "amount" INTEGER NOT NULL,
    "reason" TEXT NOT NULL,
    "result" TEXT,
    "status" "CreditRefundRequestStatus" NOT NULL DEFAULT 'PENDING',

    CONSTRAINT "CreditRefundRequest_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "CreditRefundRequest_userId_transactionKey_idx" ON "CreditRefundRequest"("userId", "transactionKey");
