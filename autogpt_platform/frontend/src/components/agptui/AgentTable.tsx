"use client";

import * as React from "react";
import { AgentTableRow, AgentTableRowProps } from "./AgentTableRow";
import { AgentTableCard } from "./AgentTableCard";
import { StoreSubmissionRequest } from "@/lib/autogpt-server-api/types";

export interface AgentTableProps {
  agents: Omit<
    AgentTableRowProps,
    | "setSelectedAgents"
    | "selectedAgents"
    | "onEditSubmission"
    | "onDeleteSubmission"
  >[];
  onEditSubmission: (submission: StoreSubmissionRequest) => void;
  onDeleteSubmission: (submission_id: string) => void;
}

export const AgentTable: React.FC<AgentTableProps> = ({
  agents,
  onEditSubmission,
  onDeleteSubmission,
}) => {
  // Use state to track selected agents
  const [selectedAgents, setSelectedAgents] = React.useState<Set<string>>(
    new Set(),
  );

  // Handle select all checkbox
  const handleSelectAll = React.useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.checked) {
        setSelectedAgents(new Set(agents.map((agent) => agent.agent_id)));
      } else {
        setSelectedAgents(new Set());
      }
    },
    [agents],
  );

  return (
    <div className="w-full">
      {/* Table header - Hide on mobile */}
      <div className="hidden flex-col md:flex">
        <div className="border-t border-neutral-300 dark:border-neutral-700" />
        <div className="flex items-center px-4 py-2">
          <div className="flex items-center">
            <div className="flex min-w-[120px] items-center">
              <input
                type="checkbox"
                id="selectAllAgents"
                aria-label="Select all agents"
                className="mr-4 h-5 w-5 rounded border-2 border-neutral-400 dark:border-neutral-600"
                checked={
                  selectedAgents.size === agents.length && agents.length > 0
                }
                onChange={handleSelectAll}
              />
              <label
                htmlFor="selectAllAgents"
                className="text-sm font-medium text-neutral-800 dark:text-neutral-200"
              >
                Select all
              </label>
            </div>
          </div>
          <div className="ml-2 grid w-full grid-cols-[400px_150px_150px_100px_100px_50px] items-center">
            <div className="text-sm font-medium text-neutral-800 dark:text-neutral-200">
              Agent info
            </div>
            <div className="text-sm font-medium text-neutral-800 dark:text-neutral-200">
              Date submitted
            </div>
            <div className="text-sm font-medium text-neutral-800 dark:text-neutral-200">
              Status
            </div>
            <div className="text-right text-sm font-medium text-neutral-800 dark:text-neutral-200">
              Runs
            </div>
            <div className="text-right text-sm font-medium text-neutral-800 dark:text-neutral-200">
              Reviews
            </div>
            <div></div>
          </div>
        </div>
        <div className="border-b border-neutral-300 dark:border-neutral-700" />
      </div>

      {/* Table body */}
      {agents.length > 0 ? (
        <div className="flex flex-col">
          {agents.map((agent, index) => (
            <div key={agent.id} className="md:block">
              <AgentTableRow
                {...agent}
                selectedAgents={selectedAgents}
                setSelectedAgents={setSelectedAgents}
                onEditSubmission={onEditSubmission}
                onDeleteSubmission={onDeleteSubmission}
              />
              <div className="block md:hidden">
                <AgentTableCard
                  {...agent}
                  onEditSubmission={onEditSubmission}
                />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="py-4 text-center font-['Geist'] text-base text-neutral-600 dark:text-neutral-400">
          No agents available. Create your first agent to get started!
        </div>
      )}
    </div>
  );
};
