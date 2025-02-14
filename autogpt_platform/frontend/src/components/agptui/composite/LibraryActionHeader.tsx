"use client";
import { LibrarySearchBar } from "@/components/agptui/LibrarySearchBar";
import LibraryNotificationDropdown from "../LibraryNotificationDropdown";
import { LibraryUploadAgent } from "../LibraryUploadAgent";

interface LibraryActionHeaderProps {}

/**
 * LibraryActionHeader component - Renders a header with search, notifications and filters
 */
const LibraryActionHeader: React.FC<LibraryActionHeaderProps> = ({}) => {
  return (
    <>
      <div className="mb-[32px] hidden items-start justify-between bg-neutral-50 md:flex">
        <LibraryNotificationDropdown />
        <LibrarySearchBar />
        <LibraryUploadAgent />
      </div>

      {/* Mobile and tablet */}
      <div className="flex flex-col gap-4 bg-neutral-50 p-4 pt-[52px] md:hidden">
        <div className="flex w-full justify-between">
          <LibraryNotificationDropdown />
          <LibraryUploadAgent />
        </div>

        <div className="flex items-center justify-center">
          <LibrarySearchBar />
        </div>
      </div>
    </>
  );
};

export default LibraryActionHeader;
