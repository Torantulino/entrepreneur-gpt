import LibraryActionHeader from "@/components/agptui/composite/LibraryActionHeader";
import LibraryAgentListContainer from "@/components/agptui/composite/LibraryAgentListContainer";

/**
 * LibraryPage Component
 * Main component that manages the library interface including agent listing and actions
 */

const LibraryPage = () => {
  return (
    <main className="mx-auto w-screen max-w-[1600px] space-y-[16px] bg-neutral-50 p-4 px-2 dark:bg-neutral-900 sm:px-8 md:px-12">
      {/* Header section containing notifications, search functionality, agent count, filters and upload mechanism */}
      <LibraryActionHeader />

      {/* Content section displaying agent list with counter and filtering options */}
      <LibraryAgentListContainer />
    </main>
  );
};

export default LibraryPage;
