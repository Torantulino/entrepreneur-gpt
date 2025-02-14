import React from "react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { GraphExecutionMeta } from "@/lib/autogpt-server-api";

export const FlowRunStatusBadge: React.FC<{
  status: GraphExecutionMeta["status"];
  className?: string;
}> = ({ status, className }) => (
  <Badge
    variant="default"
    className={cn(
      status === "RUNNING"
        ? "bg-blue-500 dark:bg-blue-700"
        : status === "QUEUED"
          ? "bg-yellow-500 dark:bg-yellow-600"
          : status === "COMPLETED"
            ? "bg-green-500 dark:bg-green-600"
            : "bg-red-500 dark:bg-red-700",
      className,
    )}
  >
    {status}
  </Badge>
);
