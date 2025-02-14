import React, { useState } from "react";
import { GraphExecutionMeta, GraphMeta } from "@/lib/autogpt-server-api";
import { CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { FlowRunsTimeline } from "@/components/monitor/FlowRunsTimeline";

export const FlowRunsStatus: React.FC<{
  flows: GraphMeta[];
  executions: GraphExecutionMeta[];
  title?: string;
  className?: string;
}> = ({ flows, executions: executions, title, className }) => {
  /* "dateMin": since the first flow in the dataset
   * number > 0: custom date (unix timestamp)
   * number < 0: offset relative to Date.now() (in seconds) */
  const [selected, setSelected] = useState<Date>();
  const [statsSince, setStatsSince] = useState<number | "dataMin">(-24 * 3600);
  const statsSinceTimestamp = // unix timestamp or null
    typeof statsSince == "string"
      ? null
      : statsSince < 0
        ? Date.now() + statsSince * 1000
        : statsSince;
  const filteredFlowRuns =
    statsSinceTimestamp != null
      ? executions.filter((fr) => fr.started_at > statsSinceTimestamp)
      : executions;

  return (
    <div className={className}>
      <div className="flex flex-row items-center justify-between">
        <CardTitle>{title || "Stats"}</CardTitle>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setStatsSince(-2 * 3600)}
          >
            2h
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setStatsSince(-8 * 3600)}
          >
            8h
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setStatsSince(-24 * 3600)}
          >
            24h
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setStatsSince(-7 * 24 * 3600)}
          >
            7d
          </Button>
          <Popover>
            <PopoverTrigger asChild>
              <Button variant={"outline"} size="sm">
                Custom
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={selected}
                onSelect={(_, selectedDay) => {
                  setSelected(selectedDay);
                  setStatsSince(selectedDay.getTime());
                }}
              />
            </PopoverContent>
          </Popover>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setStatsSince("dataMin")}
          >
            All
          </Button>
        </div>
      </div>
      <FlowRunsTimeline
        flows={flows}
        executions={executions}
        dataMin={statsSince}
        className="mt-3"
      />
      <hr className="my-4" />
      <div>
        <p>
          <strong>Total runs:</strong> {filteredFlowRuns.length}
        </p>
        <p>
          <strong>Total run time:</strong>{" "}
          {filteredFlowRuns.reduce(
            (total, run) => total + run.total_run_time,
            0,
          )}{" "}
          seconds
        </p>
        {/* <p><strong>Total cost:</strong> €1,23</p> */}
      </div>
    </div>
  );
};
export default FlowRunsStatus;
