"use client";

import * as React from "react";
import Image from "next/image";
import { Button } from "../agptui/Button";
import { IconClose } from "../ui/icons";

export interface Agent {
  name: string;
  id: string;
  version: number;
  lastEdited: string;
  imageSrc: string;
}

interface PublishAgentSelectProps {
  agents: Agent[];
  onSelect: (agentId: string, agentVersion: number) => void;
  onCancel: () => void;
  onNext: (agentId: string, agentVersion: number) => void;
  onClose: () => void;
  onOpenBuilder: () => void;
}

export const PublishAgentSelect: React.FC<PublishAgentSelectProps> = ({
  agents,
  onSelect,
  onCancel,
  onNext,
  onClose,
  onOpenBuilder,
}) => {
  const [selectedAgent, setSelectedAgent] = React.useState<string | null>(null);
  const [selectedAgentId, setSelectedAgentId] = React.useState<string | null>(
    null,
  );
  const [selectedAgentVersion, setSelectedAgentVersion] = React.useState<
    number | null
  >(null);

  const handleAgentClick = (
    agentName: string,
    agentId: string,
    agentVersion: number,
  ) => {
    setSelectedAgent(agentName);
    setSelectedAgentId(agentId);
    setSelectedAgentVersion(agentVersion);
    onSelect(agentId, agentVersion);
  };

  return (
    <div className="mx-auto flex w-full max-w-[900px] flex-col rounded-3xl bg-white shadow-lg dark:bg-gray-800">
      <div className="relative border-b border-slate-200 p-4 dark:border-slate-700 sm:p-6">
        <div className="absolute right-4 top-4">
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 transition-colors hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600"
            aria-label="Close"
          >
            <IconClose
              size="default"
              className="text-neutral-600 dark:text-neutral-400"
            />
          </button>
        </div>
        <div className="text-center">
          <h3 className="font-poppins text-2xl font-semibold text-neutral-900 dark:text-neutral-100">
            Publish Agent
          </h3>
          <p className="font-geist text-sm font-normal text-neutral-600 dark:text-neutral-400">
            Select your project that you&apos;d like to publish
          </p>
        </div>
      </div>

      {agents.length === 0 ? (
        <div className="inline-flex h-[370px] flex-col items-center justify-center gap-[29px] px-4 py-5 sm:px-6">
          <div className="w-full text-center font-['Geist'] text-lg font-normal leading-7 text-neutral-600 dark:text-neutral-400 sm:w-[573px] sm:text-xl">
            Uh-oh.. It seems like you don&apos;t have any agents in your
            library.
            <br />
            We&apos;d suggest you to create an agent in our builder first
          </div>
          <Button
            onClick={onOpenBuilder}
            size="lg"
            className="bg-neutral-800 text-white hover:bg-neutral-900"
          >
            Open builder
          </Button>
        </div>
      ) : (
        <>
          <div className="flex-grow overflow-hidden p-4 sm:p-6">
            <h3 className="sr-only">List of agents</h3>
            <div
              className="h-[300px] overflow-y-auto pr-2 sm:h-[400px] md:h-[500px]"
              role="region"
              aria-labelledby="agentListHeading"
            >
              <div id="agentListHeading" className="sr-only">
                Scrollable list of agents
              </div>
              <div className="p-2">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {agents.map((agent) => (
                    <div
                      key={agent.id}
                      className={`cursor-pointer overflow-hidden rounded-2xl transition-all ${
                        selectedAgentId === agent.id
                          ? "shadow-lg ring-4 ring-violet-600"
                          : "hover:shadow-md"
                      }`}
                      onClick={() =>
                        handleAgentClick(agent.name, agent.id, agent.version)
                      }
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          handleAgentClick(agent.name, agent.id, agent.version);
                        }
                      }}
                      tabIndex={0}
                      role="button"
                      aria-pressed={selectedAgentId === agent.id}
                    >
                      <div className="relative h-32 bg-gray-100 dark:bg-gray-700 sm:h-40">
                        <Image
                          src={agent.imageSrc}
                          alt={agent.name}
                          fill
                          style={{ objectFit: "cover" }}
                        />
                      </div>
                      <div className="p-3">
                        <p className="font-poppins text-base font-medium leading-normal text-neutral-800 dark:text-neutral-100 sm:text-base">
                          {agent.name}
                        </p>
                        <small className="font-geist text-xs font-normal leading-[14px] text-neutral-500 dark:text-neutral-400 sm:text-sm">
                          Edited {agent.lastEdited}
                        </small>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-between gap-4 border-t border-slate-200 p-4 dark:border-slate-700 sm:p-6">
            <Button
              onClick={onCancel}
              size="default"
              className="w-full sm:flex-1"
            >
              Back
            </Button>
            <Button
              onClick={() => {
                if (selectedAgentId && selectedAgentVersion) {
                  onNext(selectedAgentId, selectedAgentVersion);
                }
              }}
              disabled={!selectedAgentId || !selectedAgentVersion}
              size="default"
              className="w-full bg-neutral-800 text-white hover:bg-neutral-900 sm:flex-1"
            >
              Next
            </Button>
          </div>
        </>
      )}
    </div>
  );
};
