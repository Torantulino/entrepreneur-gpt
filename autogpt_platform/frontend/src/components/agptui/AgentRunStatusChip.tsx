import React from "react";
import { Badge } from "@/components/ui/badge";

export type AgentRunStatus =
  | "success"
  | "failed"
  | "queued"
  | "running"
  | "stopped"
  | "scheduled"
  | "draft";

const statusData: Record<
  AgentRunStatus,
  { label: string; variant: keyof typeof statusStyles }
> = {
  success: { label: "Success", variant: "success" },
  running: { label: "Running", variant: "info" },
  failed: { label: "Failed", variant: "destructive" },
  queued: { label: "Queued", variant: "warning" },
  draft: { label: "Draft", variant: "secondary" },
  stopped: { label: "Stopped", variant: "secondary" },
  scheduled: { label: "Scheduled", variant: "secondary" },
};

const statusStyles = {
  success:
    "bg-green-100 text-green-800 hover:bg-green-100 hover:text-green-800",
  destructive: "bg-red-100 text-red-800 hover:bg-red-100 hover:text-red-800",
  warning:
    "bg-yellow-100 text-yellow-800 hover:bg-yellow-100 hover:text-yellow-800",
  info: "bg-blue-100 text-blue-800 hover:bg-blue-100 hover:text-blue-800",
  secondary:
    "bg-slate-100 text-slate-800 hover:bg-slate-100 hover:text-slate-800",
};

export default function AgentRunStatusChip({
  status,
}: {
  status: AgentRunStatus;
}): React.ReactElement {
  return (
    <Badge
      variant="secondary"
      className={`text-xs font-medium ${statusStyles[statusData[status].variant]} rounded-[45px] px-[9px] py-[3px]`}
    >
      {statusData[status].label}
    </Badge>
  );
}
