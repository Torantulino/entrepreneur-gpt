"use client";
import { LibrarySearchBar } from "@/components/agptui/LibrarySearchBar";
import { LibraryNotificationDropdown } from "../LibraryNotificationDropdown";
import { LibraryUploadAgent } from "../LibraryUploadAgent";
import { motion, useScroll, useTransform } from "framer-motion";
import { cn } from "@/lib/utils";
import { useEffect, useState, useCallback } from "react";
import LibraryAgentFilter from "../LibraryAgentFilter";
import { useLibraryPageContext } from "../providers/LibraryAgentProvider";

interface LibraryActionHeaderProps {}

// Constants for header animation behavior
const SCROLL_THRESHOLD = 30;
const INITIAL_HEIGHT = 100;
const COLLAPSED_HEIGHT = 50;
const TRANSITION_DURATION = 0.3;

/**
 * LibraryActionHeader component - Renders a sticky header with search, notifications and filters
 * Animates and collapses based on scroll position
 */
const LibraryActionHeader: React.FC<LibraryActionHeaderProps> = ({}) => {
  const { scrollY } = useScroll();
  const [scrollPosition, setScrollPosition] = useState(0);
  const { agents } = useLibraryPageContext();

  const height = useTransform(
    scrollY,
    [0, 100],
    [INITIAL_HEIGHT, COLLAPSED_HEIGHT],
  );

  const handleScroll = useCallback((currentY: number) => {
    setScrollPosition(currentY);
  }, []);

  useEffect(() => {
    const unsubscribe = scrollY.on("change", handleScroll);
    return () => unsubscribe();
  }, [scrollY, handleScroll]);

  // Calculate animation offsets based on scroll position
  const getScrollAnimation = (offsetX: number, offsetY: number) => ({
    x: scrollPosition > SCROLL_THRESHOLD ? offsetX : 0,
    y: scrollPosition > SCROLL_THRESHOLD ? offsetY : 0,
  });

  return (
    <>
      <div className="sticky top-16 z-[10] hidden items-start justify-between bg-neutral-50 pb-4 md:flex">
        <motion.div
          className={cn("relative flex-1 space-y-[32px]")}
          style={{ height }}
          transition={{ duration: TRANSITION_DURATION }}
        >
          <LibraryNotificationDropdown />

          <motion.div
            className="flex items-center gap-[10px] p-2"
            animate={getScrollAnimation(60, -76)}
          >
            <span className="w-[96px] font-poppin text-[18px] font-semibold leading-[28px] text-neutral-800">
              My agents
            </span>
            <span className="w-[70px] font-sans text-[14px] font-normal leading-6">
              {agents.length} agents
            </span>
          </motion.div>
        </motion.div>

        <LibrarySearchBar />
        <motion.div
          className="flex flex-1 flex-col items-end space-y-[32px]"
          style={{ height }}
          transition={{ duration: TRANSITION_DURATION }}
        >
          <LibraryUploadAgent />
          <motion.div
            className="flex items-center gap-[10px] pl-2 pr-2 font-sans text-[14px] font-[500] leading-[24px] text-neutral-600"
            animate={getScrollAnimation(-60, -68)}
          >
            <LibraryAgentFilter />
          </motion.div>
        </motion.div>
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

        <div className="flex w-full justify-between">
          <div className="flex items-center gap-2">
            <span className="font-poppin text-[18px] font-semibold leading-[28px] text-neutral-800">
              My agents
            </span>
            <span className="font-sans text-[14px] font-normal leading-6">
              {agents.length} agents
            </span>
          </div>
          <LibraryAgentFilter />
        </div>
      </div>
    </>
  );
};

export default LibraryActionHeader;
