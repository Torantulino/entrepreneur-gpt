/*
  Warnings:

  - You are about to drop the `UserAgent` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "UserAgent" DROP CONSTRAINT "UserAgent_agentId_agentVersion_fkey";

-- DropForeignKey
ALTER TABLE "UserAgent" DROP CONSTRAINT "UserAgent_agentPresetId_fkey";

-- DropForeignKey
ALTER TABLE "UserAgent" DROP CONSTRAINT "UserAgent_userId_fkey";

-- DropTable
DROP TABLE "UserAgent";

-- CreateTable
CREATE TABLE "LibraryAgent" (
    "id" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "userId" TEXT NOT NULL,
    "agentId" TEXT NOT NULL,
    "agentVersion" INTEGER NOT NULL,
    "agentPresetId" TEXT,
    "isFavorite" BOOLEAN NOT NULL DEFAULT false,
    "isCreatedByUser" BOOLEAN NOT NULL DEFAULT false,
    "isArchived" BOOLEAN NOT NULL DEFAULT false,
    "isDeleted" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "LibraryAgent_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "LibraryAgent_userId_idx" ON "LibraryAgent"("userId");

-- AddForeignKey
ALTER TABLE "LibraryAgent" ADD CONSTRAINT "LibraryAgent_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "LibraryAgent" ADD CONSTRAINT "LibraryAgent_agentId_agentVersion_fkey" FOREIGN KEY ("agentId", "agentVersion") REFERENCES "AgentGraph"("id", "version") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "LibraryAgent" ADD CONSTRAINT "LibraryAgent_agentPresetId_fkey" FOREIGN KEY ("agentPresetId") REFERENCES "AgentPreset"("id") ON DELETE SET NULL ON UPDATE CASCADE;
