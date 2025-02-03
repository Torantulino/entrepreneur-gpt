-- AlterTable
ALTER TABLE "LibraryAgent" ADD COLUMN     "creatorId" TEXT,
ADD COLUMN     "image_url" TEXT;

-- AddForeignKey
ALTER TABLE "LibraryAgent" ADD CONSTRAINT "LibraryAgent_creatorId_fkey" FOREIGN KEY ("creatorId") REFERENCES "Profile"("id") ON DELETE SET NULL ON UPDATE CASCADE;
