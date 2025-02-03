"use client";

import * as React from "react";
import Image from "next/image";
import { IconStarFilled, IconMore, IconEdit } from "@/components/ui/icons";
import { Status, StatusType } from "./Status";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { TrashIcon } from "@radix-ui/react-icons";
import { StoreSubmissionRequest } from "@/lib/autogpt-server-api/types";

export interface AgentTableRowProps {
  agent_id: string;
  agent_version: number;
  agentName: string;
  sub_heading: string;
  description: string;
  imageSrc: string[];
  date_submitted: string;
  status: StatusType;
  runs: number;
  rating: number;
  dateSubmitted: string;
  id: number;
  selectedAgents: Set<string>;
  setSelectedAgents: React.Dispatch<React.SetStateAction<Set<string>>>;
  onEditSubmission: (submission: StoreSubmissionRequest) => void;
  onDeleteSubmission: (submission_id: string) => void;
}

export const AgentTableRow: React.FC<AgentTableRowProps> = ({
  agent_id,
  agent_version,
  agentName,
  sub_heading,
  description,
  imageSrc,
  dateSubmitted,
  status,
  runs,
  rating,
  id,
  selectedAgents,
  setSelectedAgents,
  onEditSubmission,
  onDeleteSubmission,
}) => {
  // Create a unique ID for the checkbox
  const checkboxId = `agent-${id}-checkbox`;

  const handleEdit = React.useCallback(() => {
    onEditSubmission({
      agent_id,
      agent_version,
      slug: "",
      name: agentName,
      sub_heading,
      description,
      image_urls: imageSrc,
      categories: [],
    } satisfies StoreSubmissionRequest);
  }, [
    agent_id,
    agent_version,
    agentName,
    sub_heading,
    description,
    imageSrc,
    onEditSubmission,
  ]);

  const handleDelete = React.useCallback(() => {
    onDeleteSubmission(agent_id);
  }, [agent_id, onDeleteSubmission]);

  const handleCheckboxChange = React.useCallback(() => {
    if (selectedAgents.has(agent_id)) {
      selectedAgents.delete(agent_id);
    } else {
      selectedAgents.add(agent_id);
    }
    setSelectedAgents(new Set(selectedAgents));
  }, [agent_id, selectedAgents, setSelectedAgents]);

  return (
    <div className="hidden items-center border-b border-neutral-300 px-4 py-4 hover:bg-neutral-50 dark:border-neutral-700 dark:hover:bg-neutral-800 md:flex">
      <div className="flex items-center">
        <div className="flex items-center">
          <input
            type="checkbox"
            id={checkboxId}
            aria-label={`Select ${agentName}`}
            className="mr-4 h-5 w-5 rounded border-2 border-neutral-400 dark:border-neutral-600"
            checked={selectedAgents.has(agent_id)}
            onChange={handleCheckboxChange}
          />
          {/* Single label instead of multiple */}
          <label htmlFor={checkboxId} className="sr-only">
            Select {agentName}
          </label>
        </div>
      </div>

      <div className="grid w-full grid-cols-[minmax(400px,1fr)_180px_140px_100px_100px_40px] items-center gap-4">
        {/* Agent info column */}
        <div className="flex items-center gap-4">
          <div className="relative h-[70px] w-[125px] overflow-hidden rounded-[10px] bg-[#d9d9d9] dark:bg-neutral-700">
            <Image
              src={imageSrc?.[0] ?? "/nada.png"}
              alt={agentName}
              fill
              style={{ objectFit: "cover" }}
            />
          </div>
          <div className="flex flex-col">
            <h3 className="text-[15px] font-medium text-neutral-800 dark:text-neutral-200">
              {agentName}
            </h3>
            <p className="line-clamp-2 text-sm text-neutral-600 dark:text-neutral-400">
              {description}
            </p>
          </div>
        </div>

        {/* Date column */}
        <div className="pl-14 text-sm text-neutral-600 dark:text-neutral-400">
          {dateSubmitted}
        </div>

        {/* Status column */}
        <div>
          <Status status={status} />
        </div>

        {/* Runs column */}
        <div className="text-right text-sm text-neutral-600 dark:text-neutral-400">
          {runs?.toLocaleString() ?? "0"}
        </div>

        {/* Reviews column */}
        <div className="text-right">
          {rating ? (
            <div className="flex items-center justify-end gap-1">
              <span className="text-sm font-medium text-neutral-800 dark:text-neutral-200">
                {rating.toFixed(1)}
              </span>
              <IconStarFilled className="h-4 w-4 text-neutral-800 dark:text-neutral-200" />
            </div>
          ) : (
            <span className="text-sm text-neutral-600 dark:text-neutral-400">
              No reviews
            </span>
          )}
        </div>

        {/* Actions - Three dots menu */}
        <div className="flex justify-end">
          <DropdownMenu.Root>
            <DropdownMenu.Trigger>
              <button className="rounded-full p-1 hover:bg-neutral-100 dark:hover:bg-neutral-700">
                <IconMore className="h-5 w-5 text-neutral-800 dark:text-neutral-200" />
              </button>
            </DropdownMenu.Trigger>
            <DropdownMenu.Content className="z-10 rounded-xl border bg-white p-1 shadow-md dark:bg-gray-800">
              <DropdownMenu.Item
                onSelect={handleEdit}
                className="flex cursor-pointer items-center rounded-md px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <IconEdit className="mr-2 h-5 w-5 dark:text-gray-100" />
                <span className="dark:text-gray-100">Edit</span>
              </DropdownMenu.Item>
              <DropdownMenu.Separator className="my-1 h-px bg-gray-300 dark:bg-gray-600" />
              <DropdownMenu.Item
                onSelect={handleDelete}
                className="flex cursor-pointer items-center rounded-md px-3 py-2 text-red-500 hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <TrashIcon className="mr-2 h-5 w-5 text-red-500 dark:text-red-400" />
                <span className="dark:text-red-400">Delete</span>
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Root>
        </div>
      </div>
    </div>
  );
};
