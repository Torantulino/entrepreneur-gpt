"use client";

import * as React from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDownIcon } from "@radix-ui/react-icons";

const sortOptions: SortOption[] = [
  { label: "Most Recent", value: "recent" },
  { label: "Most Runs", value: "runs" },
  { label: "Highest Rated", value: "rating" },
];

interface SortOption {
  label: string;
  value: string;
}

export const SortDropdown: React.FC<{
  onSort: (sortValue: string) => void;
}> = ({ onSort }) => {
  const [selected, setSelected] = React.useState(sortOptions[0]);

  const handleSelect = (option: SortOption) => {
    setSelected(option);
    onSort(option.value);
    console.log(`Sorting by: ${option.label} (${option.value})`);
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="flex items-center gap-1.5 focus:outline-hidden">
        <span className="font-geist text-base text-neutral-800 dark:text-neutral-200">
          Sort by
        </span>
        <span className="font-geist text-base text-neutral-800 dark:text-neutral-200">
          {selected.label}
        </span>
        <ChevronDownIcon className="h-4 w-4 text-neutral-800 dark:text-neutral-200" />
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="end"
        className="w-[200px] rounded-lg bg-white shadow-lg dark:bg-neutral-800"
      >
        {sortOptions.map((option) => (
          <DropdownMenuItem
            key={option.value}
            className={`cursor-pointer px-4 py-2 text-base hover:bg-neutral-100 dark:hover:bg-neutral-700 ${
              selected.value === option.value
                ? "font-medium text-neutral-800 dark:text-neutral-200"
                : "text-neutral-600 dark:text-neutral-400"
            }`}
            onClick={() => handleSelect(option)}
          >
            {option.label}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
