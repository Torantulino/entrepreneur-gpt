"use client";

import * as React from "react";
import { IconClose } from "../ui/icons";
import Image from "next/image";
import { Button } from "../agptui/Button";

interface PublishAgentAwaitingReviewProps {
  agentName: string;
  subheader: string;
  description: string;
  thumbnailSrc?: string;
  onClose: () => void;
  onDone: () => void;
  onViewProgress: () => void;
}

export const PublishAgentAwaitingReview: React.FC<
  PublishAgentAwaitingReviewProps
> = ({
  agentName,
  subheader,
  description,
  thumbnailSrc,
  onClose,
  onDone,
  onViewProgress,
}) => {
  return (
    <div
      className="inline-flex min-h-screen w-full flex-col items-center justify-center rounded-none bg-white dark:bg-neutral-900 sm:h-auto sm:min-h-[824px] sm:rounded-3xl"
      role="dialog"
      aria-labelledby="modal-title"
    >
      <div className="relative h-[180px] w-full rounded-none bg-white dark:bg-neutral-800 sm:h-[140px] sm:rounded-t-3xl">
        <div className="absolute left-0 top-[40px] flex w-full flex-col items-center justify-start px-6 sm:top-[40px]">
          <div
            id="modal-title"
            className="mb-4 text-center font-['Poppins'] text-xl font-semibold leading-relaxed text-neutral-900 dark:text-neutral-100 sm:mb-2 sm:text-2xl"
          >
            Agent is awaiting review
          </div>
          <div className="max-w-[280px] text-center font-['Inter'] text-sm font-normal leading-relaxed text-slate-500 dark:text-slate-400 sm:max-w-none">
            In the meantime you can check your progress on your Creator
            Dashboard page
          </div>
        </div>
        <button
          onClick={onClose}
          className="absolute right-4 top-4 flex h-[38px] w-[38px] items-center justify-center rounded-full bg-gray-100 transition-colors hover:bg-gray-200 dark:bg-neutral-700 dark:hover:bg-neutral-600"
          aria-label="Close dialog"
        >
          <IconClose
            size="default"
            className="text-neutral-600 dark:text-neutral-300"
          />
        </button>
      </div>

      <div className="flex flex-1 flex-col items-center gap-8 px-6 py-6 sm:gap-6">
        <div className="mt-4 flex w-full flex-col items-center gap-6 sm:mt-0 sm:gap-4">
          <div className="flex flex-col items-center gap-3 sm:gap-2">
            <div className="text-center font-['Geist'] text-lg font-semibold leading-7 text-neutral-800 dark:text-neutral-200">
              {agentName}
            </div>
            <div className="max-w-[280px] text-center font-['Geist'] text-base font-normal leading-normal text-neutral-600 dark:text-neutral-400 sm:max-w-none">
              {subheader}
            </div>
          </div>

          <div
            className="h-[280px] w-full rounded-xl bg-neutral-200 dark:bg-neutral-700 sm:h-[350px]"
            role="img"
            aria-label={
              thumbnailSrc ? "Agent thumbnail" : "Thumbnail placeholder"
            }
          >
            {thumbnailSrc && (
              <Image
                src={thumbnailSrc}
                alt="Agent thumbnail"
                width={500}
                height={350}
                className="h-full w-full rounded-xl object-cover"
              />
            )}
          </div>

          <div
            className="h-[150px] w-full overflow-y-auto font-['Geist'] text-base font-normal leading-normal text-neutral-600 dark:text-neutral-400 sm:h-[180px]"
            tabIndex={0}
            role="region"
            aria-label="Agent description"
          >
            {description}
          </div>
        </div>
      </div>

      <div className="flex w-full flex-col items-center justify-center gap-4 border-t border-slate-200 p-6 dark:border-slate-700 sm:flex-row">
        <Button
          onClick={onDone}
          className="h-12 w-full rounded-[59px] sm:flex-1"
        >
          Done
        </Button>
        <Button
          onClick={onViewProgress}
          className="h-12 w-full rounded-[59px] bg-neutral-800 text-white hover:bg-neutral-900 dark:bg-neutral-700 dark:text-neutral-100 dark:hover:bg-neutral-600 sm:flex-1"
        >
          View progress
        </Button>
      </div>
    </div>
  );
};
