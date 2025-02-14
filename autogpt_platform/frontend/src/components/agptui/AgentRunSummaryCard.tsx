import React from "react";
import moment from "moment";
import { MoreVertical } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import AgentRunStatusChip, { AgentRunStatus } from "./AgentRunStatusChip";

export type AgentRunSummaryProps = {
  agentID: string;
  agentRunID: string;
  status: AgentRunStatus;
  title: string;
  timestamp: number | Date;
  selected?: boolean;
  onClick?: () => void;
  className?: string;
};

export default function AgentRunSummaryCard({
  agentID,
  agentRunID,
  status,
  title,
  timestamp,
  selected = false,
  onClick,
  className,
}: AgentRunSummaryProps): React.ReactElement {
  return (
    <Card
      className={cn(
        "agpt-rounded-card cursor-pointer border-zinc-300",
        selected ? "agpt-card-selected" : "",
        className,
      )}
      onClick={onClick}
    >
      <CardContent className="relative p-2.5 lg:p-4">
        <AgentRunStatusChip status={status} />

        <div className="mt-5 flex items-center justify-between">
          <h3 className="truncate pr-2 text-base font-medium text-neutral-900">
            {title}
          </h3>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-5 w-5 p-0">
                <MoreVertical className="h-5 w-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem /* TODO: implement */>
                Pin into a template
              </DropdownMenuItem>
              <DropdownMenuItem /* TODO: implement */>Rename</DropdownMenuItem>
              <DropdownMenuItem /* TODO: implement */>Delete</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <p
          className="mt-1 text-sm font-normal text-neutral-500"
          title={moment(timestamp).toString()}
        >
          Ran {moment(timestamp).fromNow()}
        </p>
      </CardContent>
    </Card>
  );
}
