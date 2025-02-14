"use client";

import * as React from "react";
import { IconPlay, StarRatingIcons } from "@/components/ui/icons";
import { Separator } from "@/components/ui/separator";
import BackendAPI from "@/lib/autogpt-server-api";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useToast } from "@/components/ui/use-toast";

import useSupabase from "@/hooks/useSupabase";
import { DownloadIcon, LoaderIcon } from "lucide-react";
interface AgentInfoProps {
  name: string;
  creator: string;
  shortDescription: string;
  longDescription: string;
  rating: number;
  runs: number;
  categories: string[];
  lastUpdated: string;
  version: string;
  storeListingVersionId: string;
}

export const AgentInfo: React.FC<AgentInfoProps> = ({
  name,
  creator,
  shortDescription,
  longDescription,
  rating,
  runs,
  categories,
  lastUpdated,
  version,
  storeListingVersionId,
}) => {
  const router = useRouter();
  const api = React.useMemo(() => new BackendAPI(), []);
  const { user } = useSupabase();
  const { toast } = useToast();

  const [downloading, setDownloading] = React.useState(false);

  const handleAddToLibrary = async () => {
    try {
      await api.addAgentToLibrary(storeListingVersionId);
      console.log("Agent added to library successfully");
      router.push("/monitoring");
    } catch (error) {
      console.error("Failed to add agent to library:", error);
    }
  };

  const handleDownloadToLibrary = async () => {
    const downloadAgent = async (): Promise<void> => {
      setDownloading(true);
      try {
        const file = await api.downloadStoreAgent(storeListingVersionId);

        // Similar to Marketplace v1
        const jsonData = JSON.stringify(file, null, 2);
        // Create a Blob from the file content
        const blob = new Blob([jsonData], { type: "application/json" });

        // Create a temporary URL for the Blob
        const url = window.URL.createObjectURL(blob);

        // Create a temporary anchor element
        const a = document.createElement("a");
        a.href = url;
        a.download = `agent_${storeListingVersionId}.json`; // Set the filename

        // Append the anchor to the body, click it, and remove it
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        // Revoke the temporary URL
        window.URL.revokeObjectURL(url);

        toast({
          title: "Download Complete",
          description: "Your agent has been successfully downloaded.",
        });
      } catch (error) {
        console.error(`Error downloading agent:`, error);
        throw error;
      }
    };
    await downloadAgent();
    setDownloading(false);
  };

  return (
    <div className="w-full max-w-[396px] px-4 sm:px-6 lg:w-[396px] lg:px-0">
      {/* Title */}
      <div className="mb-3 w-full font-poppins text-2xl font-medium leading-normal text-neutral-900 dark:text-neutral-100 sm:text-3xl lg:mb-4 lg:text-[35px] lg:leading-10">
        {name}
      </div>

      {/* Creator */}
      <div className="mb-3 flex w-full items-center gap-1.5 lg:mb-4">
        <div className="font-geist text-base font-normal text-neutral-800 dark:text-neutral-200 sm:text-lg lg:text-xl">
          by
        </div>
        <Link
          href={`/marketplace/creator/${encodeURIComponent(creator)}`}
          className="font-geist text-base font-medium text-neutral-800 hover:underline dark:text-neutral-200 sm:text-lg lg:text-xl"
        >
          {creator}
        </Link>
      </div>

      {/* Short Description */}
      <div className="font-geist mb-4 line-clamp-2 w-full text-base font-normal leading-normal text-neutral-600 dark:text-neutral-300 sm:text-lg lg:mb-6 lg:text-xl lg:leading-7">
        {shortDescription}
      </div>

      {/* Run Agent Button */}
      <div className="mb-4 w-full lg:mb-[60px]">
        {user ? (
          <button
            onClick={handleAddToLibrary}
            className="inline-flex w-full items-center justify-center gap-2 rounded-[38px] bg-violet-600 px-4 py-3 transition-colors hover:bg-violet-700 sm:w-auto sm:gap-2.5 sm:px-5 sm:py-3.5 lg:px-6 lg:py-4"
          >
            <IconPlay className="h-5 w-5 text-white sm:h-5 sm:w-5 lg:h-6 lg:w-6" />
            <span className="font-poppins text-base font-medium text-neutral-50 sm:text-lg">
              Add To Library
            </span>
          </button>
        ) : (
          <button
            onClick={handleDownloadToLibrary}
            className={`inline-flex w-full items-center justify-center gap-2 rounded-[38px] px-4 py-3 transition-colors sm:w-auto sm:gap-2.5 sm:px-5 sm:py-3.5 lg:px-6 lg:py-4 ${
              downloading
                ? "bg-neutral-400"
                : "bg-violet-600 hover:bg-violet-700"
            }`}
            disabled={downloading}
          >
            {downloading ? (
              <LoaderIcon className="h-5 w-5 animate-spin text-white sm:h-5 sm:w-5 lg:h-6 lg:w-6" />
            ) : (
              <DownloadIcon className="h-5 w-5 text-white sm:h-5 sm:w-5 lg:h-6 lg:w-6" />
            )}
            <span className="font-poppins text-base font-medium text-neutral-50 sm:text-lg">
              {downloading ? "Downloading..." : "Download Agent as File"}
            </span>
          </button>
        )}
      </div>

      {/* Rating and Runs */}
      <div className="mb-4 flex w-full items-center justify-between lg:mb-[44px]">
        <div className="flex items-center gap-1.5 sm:gap-2">
          <span className="font-geist whitespace-nowrap text-base font-semibold text-neutral-800 dark:text-neutral-200 sm:text-lg">
            {rating.toFixed(1)}
          </span>
          <div className="flex gap-0.5">{StarRatingIcons(rating)}</div>
        </div>
        <div className="font-geist whitespace-nowrap text-base font-semibold text-neutral-800 dark:text-neutral-200 sm:text-lg">
          {runs.toLocaleString()} runs
        </div>
      </div>

      {/* Separator */}
      <Separator className="mb-4 lg:mb-[44px]" />

      {/* Description Section */}
      <div className="mb-4 w-full lg:mb-[36px]">
        <div className="font-geist decoration-skip-ink-none mb-1.5 text-base font-medium leading-6 text-neutral-800 dark:text-neutral-200 sm:mb-2">
          Description
        </div>
        <div className="font-geist decoration-skip-ink-none text-base font-normal leading-6 text-neutral-600 underline-offset-[from-font] dark:text-neutral-400">
          {longDescription}
        </div>
      </div>

      {/* Categories */}
      <div className="mb-4 flex w-full flex-col gap-1.5 sm:gap-2 lg:mb-[36px]">
        <div className="font-geist decoration-skip-ink-none mb-1.5 text-base font-medium leading-6 text-neutral-800 dark:text-neutral-200 sm:mb-2">
          Categories
        </div>
        <div className="flex flex-wrap gap-1.5 sm:gap-2">
          {categories.map((category, index) => (
            <div
              key={index}
              className="font-geist decoration-skip-ink-none whitespace-nowrap rounded-full border border-neutral-600 bg-white px-2 py-0.5 text-base font-normal leading-6 text-neutral-800 underline-offset-[from-font] dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-200 sm:px-[16px] sm:py-[10px]"
            >
              {category}
            </div>
          ))}
        </div>
      </div>

      {/* Version History */}
      <div className="flex w-full flex-col gap-0.5 sm:gap-1">
        <div className="font-geist decoration-skip-ink-none mb-1.5 text-base font-medium leading-6 text-neutral-800 dark:text-neutral-200 sm:mb-2">
          Version history
        </div>
        <div className="font-geist decoration-skip-ink-none text-base font-normal leading-6 text-neutral-600 underline-offset-[from-font] dark:text-neutral-400">
          Last updated {lastUpdated}
        </div>
        <div className="text-xs text-neutral-600 dark:text-neutral-400 sm:text-sm">
          Version {version}
        </div>
      </div>
    </div>
  );
};
