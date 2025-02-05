"use client";
import { Search, X } from "lucide-react";
import { Input } from "../ui/input";
import { useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import debounce from "lodash/debounce";
import { useBackendAPI } from "@/lib/autogpt-server-api/context";
import { useLibraryPageContext } from "./providers/LibraryAgentProvider";

export const LibrarySearchBar = () => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const api = useBackendAPI();
  const { setAgentLoading, setAgents, libraryFilter, setSearchTerm } =
    useLibraryPageContext();

  const debouncedSearch = debounce(async (value: string) => {
    try {
      setAgentLoading(true);
      setSearchTerm(value);
      await new Promise((resolve) => setTimeout(resolve, 1000));
      const response = await api.librarySearchAgent(value, libraryFilter);
      setAgents(response.agents);
      setAgentLoading(false);
    } catch (error) {
      console.error("Search failed:", error);
    }
  }, 300);
  const handleSearchInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const searchTerm = e.target.value;
    debouncedSearch(searchTerm);
  };

  return (
    <div
      onClick={() => inputRef.current?.focus()}
      className="relative z-[21] mx-auto flex h-[50px] w-full max-w-[500px] flex-1 cursor-pointer items-center rounded-[45px] bg-[#EDEDED] px-[24px] py-[10px]"
    >
      <div className="w-[30px] overflow-hidden">
        <AnimatePresence mode="wait">
          {!isFocused ? (
            <motion.div
              key="search"
              initial={{ x: -50 }}
              animate={{ x: 0 }}
              exit={{ x: -50 }}
              transition={{
                duration: 0.2,
                ease: "easeInOut",
              }}
            >
              <Search
                className="h-[29px] w-[29px] text-neutral-900"
                strokeWidth={1.25}
              />
            </motion.div>
          ) : (
            <motion.div
              key="close"
              initial={{ x: 50 }}
              animate={{ x: 0 }}
              exit={{ x: 50 }}
              transition={{
                duration: 0.2,
                ease: "easeInOut",
              }}
            >
              <X
                className="h-[29px] w-[29px] cursor-pointer text-neutral-900"
                strokeWidth={1.25}
                onClick={(e) => {
                  if (inputRef.current) {
                    debouncedSearch("");
                    inputRef.current.value = "";
                    inputRef.current.blur();
                    e.preventDefault();
                  }
                  setIsFocused(false);
                }}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <Input
        ref={inputRef}
        onFocus={() => setIsFocused(true)}
        onBlur={() => !inputRef.current?.value && setIsFocused(false)}
        onChange={handleSearchInput}
        className="border-none font-sans text-[16px] font-normal leading-7 shadow-none focus:shadow-none"
        type="text"
        placeholder="Search agents"
      />
    </div>
  );
};
