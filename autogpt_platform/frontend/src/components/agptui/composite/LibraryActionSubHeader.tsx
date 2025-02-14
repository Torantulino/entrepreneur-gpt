"use client";

import LibraryAgentFilter from "../LibraryAgentFilter";
import { useLibraryPageContext } from "../providers/LibraryAgentProvider";

export const LibraryActionSubHeader = () => {
  const { agents } = useLibraryPageContext();

  return (
    <div className="flex items-center justify-between pb-[10px]">
      <div className="flex items-center gap-[10px] p-2">
        <span className="w-[96px] font-poppin text-[18px] font-semibold leading-[28px] text-neutral-800">
          My agents
        </span>
        <span className="w-[70px] font-sans text-[14px] font-normal leading-6">
          {agents.length} agents
        </span>
      </div>
      <LibraryAgentFilter />
    </div>
  );
};
