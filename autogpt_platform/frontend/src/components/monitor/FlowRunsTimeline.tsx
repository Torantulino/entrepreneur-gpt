import { GraphExecutionMeta, GraphMeta } from "@/lib/autogpt-server-api";
import {
  ComposedChart,
  DefaultLegendContentProps,
  Legend,
  Line,
  ResponsiveContainer,
  Scatter,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import moment from "moment/moment";
import { Card } from "@/components/ui/card";
import { cn, hashString } from "@/lib/utils";
import React from "react";
import { FlowRunStatusBadge } from "@/components/monitor/FlowRunStatusBadge";

export const FlowRunsTimeline = ({
  flows,
  executions,
  dataMin,
  className,
}: {
  flows: GraphMeta[];
  executions: GraphExecutionMeta[];
  dataMin: "dataMin" | number;
  className?: string;
}) => (
  /* TODO: make logarithmic? */
  <ResponsiveContainer width="100%" height={120} className={className}>
    <ComposedChart>
      <XAxis
        dataKey="time"
        type="number"
        domain={[
          typeof dataMin == "string"
            ? dataMin
            : dataMin < 0
              ? Date.now() + dataMin * 1000
              : dataMin,
          Date.now(),
        ]}
        allowDataOverflow={true}
        tickFormatter={(unixTime) => {
          const now = moment();
          const time = moment(unixTime);
          return now.diff(time, "hours") < 24
            ? time.format("HH:mm")
            : time.format("YYYY-MM-DD HH:mm");
        }}
        name="Time"
        scale="time"
      />
      <YAxis
        dataKey="_duration"
        name="Duration (s)"
        tickFormatter={(s) => (s > 90 ? `${Math.round(s / 60)}m` : `${s}s`)}
      />
      <Tooltip
        content={({ payload, label }) => {
          if (payload && payload.length) {
            const data: GraphExecutionMeta & {
              time: number;
              _duration: number;
            } = payload[0].payload;
            const flow = flows.find((f) => f.id === data.graph_id);
            return (
              <Card className="p-2 text-xs leading-normal">
                <p>
                  <strong>Agent:</strong> {flow ? flow.name : "Unknown"}
                </p>
                <div>
                  <strong>Status:</strong>&nbsp;
                  <FlowRunStatusBadge
                    status={data.status}
                    className="px-1.5 py-0"
                  />
                </div>
                <p>
                  <strong>Started:</strong>{" "}
                  {moment(data.started_at).format("YYYY-MM-DD HH:mm:ss")}
                </p>
                <p>
                  <strong>Duration / run time:</strong>{" "}
                  {formatDuration(data.duration)} /{" "}
                  {formatDuration(data.total_run_time)}
                </p>
              </Card>
            );
          }
          return null;
        }}
      />
      {flows.map((flow) => (
        <Scatter
          key={flow.id}
          data={executions
            .filter((e) => e.graph_id == flow.id)
            .map((e) => ({
              ...e,
              time: e.started_at + e.total_run_time * 1000,
              _duration: e.total_run_time,
            }))}
          name={flow.name}
          fill={`hsl(${(hashString(flow.id) * 137.5) % 360}, 70%, 50%)`}
        />
      ))}
      {executions.map((execution) => (
        <Line
          key={execution.execution_id}
          type="linear"
          dataKey="_duration"
          data={[
            { ...execution, time: execution.started_at, _duration: 0 },
            {
              ...execution,
              time: execution.ended_at,
              _duration: execution.total_run_time,
            },
          ]}
          stroke={`hsl(${(hashString(execution.graph_id) * 137.5) % 360}, 70%, 50%)`}
          strokeWidth={2}
          dot={false}
          legendType="none"
        />
      ))}
      <Legend
        content={<ScrollableLegend />}
        wrapperStyle={{
          bottom: 0,
          left: 0,
          right: 0,
          width: "100%",
          display: "flex",
          justifyContent: "center",
        }}
      />
    </ComposedChart>
  </ResponsiveContainer>
);

export default FlowRunsTimeline;

const ScrollableLegend: React.FC<
  DefaultLegendContentProps & { className?: string }
> = ({ payload, className }) => {
  return (
    <div
      className={cn(
        "space-x-3 overflow-x-auto whitespace-nowrap px-4 text-sm",
        className,
      )}
      style={{ scrollbarWidth: "none" }}
    >
      {payload?.map((entry, index) => {
        if (entry.type == "none") return;
        return (
          <span key={`item-${index}`} className="inline-flex items-center">
            <span
              className="mr-1 inline-block size-2.5 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span>{entry.value}</span>
          </span>
        );
      })}
    </div>
  );
};

function formatDuration(seconds: number): string {
  return (
    (seconds < 100 ? seconds.toPrecision(2) : Math.round(seconds)).toString() +
    "s"
  );
}
