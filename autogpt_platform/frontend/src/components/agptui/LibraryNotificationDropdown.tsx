"use client";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "./Button";
import { BellIcon, X } from "lucide-react";
import { motion, useAnimationControls } from "framer-motion";
import { useState, useEffect, useMemo } from "react";
import LibraryNotificationCard, {
  NotificationCardData,
} from "./LibraryNotificationCard";
import { cn } from "@/lib/utils";

const LibraryNotificationDropdown = () => {
  const controls = useAnimationControls();
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<
    NotificationCardData[] | null
  >(null);

  const initialNotificationData = useMemo(
    () =>
      [
        {
          type: "audio" as "audio",
          title: "Audio Processing Complete",
          id: "4",
        },
        {
          type: "text" as "text",
          title: "LinkedIn Post Generator: YouTube to Professional Content",
          id: "1",
          content:
            "As artificial intelligence (AI) continues to evolve, it's increasingly clear that AI isn't just a trend—it's reshaping the way we work, innovate, and solve complex problems. However, for many professionals, the question remains: How can I leverage AI to drive meaningful results in my own field? In this article, we'll explore how AI can empower businesses and individuals alike to be more efficient, make better decisions, and unlock new opportunities. Whether you're in tech, finance, healthcare, or any other industry, understanding the potential of AI can set you apart.",
        },
        {
          type: "image" as "image",
          title: "New Image Upload",
          id: "2",
        },
        {
          type: "video" as "video",
          title: "Video Processing Complete",
          id: "3",
        },
      ] as NotificationCardData[],
    [],
  );

  useEffect(() => {
    if (initialNotificationData) {
      setNotifications(initialNotificationData);
    }
  }, [initialNotificationData]);

  const handleHoverStart = () => {
    controls.start({
      rotate: [0, -10, 10, -10, 10, 0],
      transition: { duration: 0.5 },
    });
  };

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger className="sm:flex-1" asChild>
        <Button
          variant={open ? "library_primary" : "library_outline"}
          size="library"
          onMouseEnter={handleHoverStart}
          onMouseLeave={handleHoverStart}
          className="w-fit max-w-[161px] transition-all duration-200 ease-in-out sm:w-[161px]"
        >
          <motion.div animate={controls}>
            <BellIcon
              className="h-5 w-5 transition-all duration-200 ease-in-out sm:mr-2"
              strokeWidth={2}
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 1 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="hidden items-center transition-opacity duration-300 sm:inline-flex"
          >
            Your updates
            <span className="ml-2 text-[14px]">
              {notifications?.length || 0}
            </span>
          </motion.div>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        sideOffset={22}
        className="scroll-none relative left-[16px] h-[80vh] w-fit overflow-y-auto rounded-[26px] bg-[#C5C5CA] p-5"
      >
        <DropdownMenuLabel className="z-10 mb-4 font-sans text-[18px] text-white">
          Agent run updates
        </DropdownMenuLabel>
        <button
          className="absolute right-[10px] top-[20px] h-fit w-fit"
          onClick={() => setOpen(false)}
        >
          <X className="h-6 w-6 text-white hover:text-white/60" />
        </button>
        <div className="space-y-[12px]">
          {notifications && notifications.length ? (
            notifications.map((notification) => (
              <DropdownMenuItem key={notification.id} className="p-0">
                <LibraryNotificationCard
                  {...notification}
                  setNotifications={setNotifications}
                />
              </DropdownMenuItem>
            ))
          ) : (
            <div className="w-[464px] py-4 text-center text-white">
              No notifications present
            </div>
          )}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default LibraryNotificationDropdown;
