"use client";
import React, { useCallback, useEffect, useState } from "react";

import { GraphExecution, Schedule, GraphMeta } from "@/lib/autogpt-server-api";

import { Card } from "@/components/ui/card";
import {
  AgentFlowList,
  FlowInfo,
  FlowRunInfo,
  FlowRunsList,
  FlowRunsStats,
} from "@/components/monitor";
import { SchedulesTable } from "@/components/monitor/scheduleTable";
import { useBackendAPI } from "@/lib/autogpt-server-api/context";

const Monitor = () => {
  const [flows, setFlows] = useState<GraphMeta[]>([]);
  const [executions, setExecutions] = useState<GraphExecution[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [selectedFlow, setSelectedFlow] = useState<GraphMeta | null>(null);
  const [selectedRun, setSelectedRun] = useState<GraphExecution | null>(null);
  const [sortColumn, setSortColumn] = useState<keyof Schedule>("id");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const api = useBackendAPI();

  const fetchSchedules = useCallback(async () => {
    setSchedules(await api.listSchedules());
  }, [api]);

  const removeSchedule = useCallback(
    async (scheduleId: string) => {
      const removedSchedule = await api.deleteSchedule(scheduleId);
      setSchedules(schedules.filter((s) => s.id !== removedSchedule.id));
    },
    [schedules, api],
  );

  const fetchAgents = useCallback(() => {
    api.listLibraryAgents().then((agents) => {
      setFlows(agents);
    });
    api.getExecutions().then((executions) => {
      setExecutions(executions);
    });
  }, [api]);

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  useEffect(() => {
    fetchSchedules();
  }, [fetchSchedules]);

  useEffect(() => {
    const intervalId = setInterval(() => fetchAgents(), 5000);
    return () => clearInterval(intervalId);
  }, [fetchAgents, flows]);

  const column1 = "md:col-span-2 xl:col-span-3 xxl:col-span-2";
  const column2 = "md:col-span-3 lg:col-span-2 xl:col-span-3";
  const column3 = "col-span-full xl:col-span-4 xxl:col-span-5";

  const handleSort = (column: keyof Schedule) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortColumn(column);
      setSortDirection("asc");
    }
  };

  return (
    <div
      className="grid grid-cols-1 gap-4 p-4 md:grid-cols-5 lg:grid-cols-4 xl:grid-cols-10"
      data-testid="monitor-page"
    >
      <AgentFlowList
        className={column1}
        flows={flows}
        executions={executions}
        selectedFlow={selectedFlow}
        onSelectFlow={(f) => {
          setSelectedRun(null);
          setSelectedFlow(f.id == selectedFlow?.id ? null : (f as GraphMeta));
        }}
      />
      <FlowRunsList
        className={column2}
        flows={flows}
        executions={[
          ...(selectedFlow
            ? executions.filter((v) => v.graph_id == selectedFlow.id)
            : executions),
        ].sort((a, b) => Number(b.started_at) - Number(a.started_at))}
        selectedRun={selectedRun}
        onSelectRun={(r) =>
          setSelectedRun(r.execution_id == selectedRun?.execution_id ? null : r)
        }
      />
      {(selectedRun && (
        <FlowRunInfo
          flow={
            selectedFlow || flows.find((f) => f.id == selectedRun.graph_id)!
          }
          execution={selectedRun}
          className={column3}
        />
      )) ||
        (selectedFlow && (
          <FlowInfo
            flow={selectedFlow}
            executions={executions.filter((e) => e.graph_id == selectedFlow.id)}
            className={column3}
            refresh={() => {
              fetchAgents();
              setSelectedFlow(null);
              setSelectedRun(null);
            }}
          />
        )) || (
          <Card className={`p-6 ${column3}`}>
            <FlowRunsStats flows={flows} executions={executions} />
          </Card>
        )}
      <div className="col-span-full xl:col-span-6">
        <SchedulesTable
          schedules={schedules} // all schedules
          agents={flows} // for filtering purpose
          onRemoveSchedule={removeSchedule}
          sortColumn={sortColumn}
          sortDirection={sortDirection}
          onSort={handleSort}
        />
      </div>
    </div>
  );
};

export default Monitor;
