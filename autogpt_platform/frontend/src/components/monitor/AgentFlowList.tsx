import BackendAPI, {
  GraphExecutionMeta,
  GraphMeta,
} from "@/lib/autogpt-server-api";
import React, { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TextRenderer } from "@/components/ui/render";
import Link from "next/link";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDownIcon, EnterIcon } from "@radix-ui/react-icons";
import { AgentImportForm } from "@/components/agent-import-form";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import moment from "moment/moment";
import { DialogTitle } from "@/components/ui/dialog";

export const AgentFlowList = ({
  flows,
  executions,
  selectedFlow,
  onSelectFlow,
  className,
}: {
  flows: GraphMeta[];
  executions?: GraphExecutionMeta[];
  selectedFlow: GraphMeta | null;
  onSelectFlow: (f: GraphMeta) => void;
  className?: string;
}) => {
  return (
    <Card className={className}>
      <CardHeader className="flex-row items-center justify-between space-x-3 space-y-0">
        <CardTitle>Agents</CardTitle>

        <div className="flex items-center">
          {/* Split "Create" button */}
          <Button variant="outline" className="rounded-r-none" asChild>
            <Link href="/build">Create</Link>
          </Button>
          <Dialog>
            {/* https://ui.shadcn.com/docs/components/dialog#notes */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="outline"
                  className={"rounded-l-none border-l-0 px-2"}
                  data-testid="create-agent-dropdown"
                >
                  <ChevronDownIcon />
                </Button>
              </DropdownMenuTrigger>

              <DropdownMenuContent>
                <DialogTrigger asChild>
                  <DropdownMenuItem data-testid="import-agent-from-file">
                    <EnterIcon className="mr-2" /> Import from file
                  </DropdownMenuItem>
                </DialogTrigger>
              </DropdownMenuContent>
            </DropdownMenu>

            <DialogContent>
              <DialogHeader>
                <DialogTitle className="sr-only">Import Agent</DialogTitle>
                <h2 className="text-lg font-semibold">
                  Import an Agent from a file
                </h2>
              </DialogHeader>
              <AgentImportForm />
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>

      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              {/* <TableHead>Status</TableHead> */}
              {/* <TableHead>Last updated</TableHead> */}
              {executions && (
                <TableHead className="md:hidden lg:table-cell">
                  # of runs
                </TableHead>
              )}
              {executions && <TableHead>Last run</TableHead>}
            </TableRow>
          </TableHeader>
          <TableBody data-testid="agent-flow-list-body">
            {flows
              .map((flow) => {
                let runCount = 0,
                  lastRun: GraphExecutionMeta | null = null;
                if (executions) {
                  const _flowRuns = executions.filter(
                    (r) => r.graph_id == flow.id,
                  );
                  runCount = _flowRuns.length;
                  lastRun =
                    runCount == 0
                      ? null
                      : _flowRuns.reduce((a, c) =>
                          a.started_at > c.started_at ? a : c,
                        );
                }
                return { flow, runCount, lastRun };
              })
              .sort((a, b) => {
                if (!a.lastRun && !b.lastRun) return 0;
                if (!a.lastRun) return 1;
                if (!b.lastRun) return -1;
                return b.lastRun.started_at - a.lastRun.started_at;
              })
              .map(({ flow, runCount, lastRun }) => (
                <TableRow
                  key={flow.id}
                  data-testid={flow.id}
                  data-name={flow.name}
                  className="cursor-pointer"
                  onClick={() => onSelectFlow(flow)}
                  data-state={selectedFlow?.id == flow.id ? "selected" : null}
                >
                  <TableCell>
                    <TextRenderer value={flow.name} truncateLengthLimit={30} />
                  </TableCell>
                  {/* <TableCell><FlowStatusBadge status={flow.status ?? "active"} /></TableCell> */}
                  {/* <TableCell>
                  {flow.updatedAt ?? "???"}
                </TableCell> */}
                  {executions && (
                    <TableCell className="md:hidden lg:table-cell">
                      {runCount}
                    </TableCell>
                  )}
                  {executions &&
                    (!lastRun ? (
                      <TableCell />
                    ) : (
                      <TableCell title={moment(lastRun.started_at).toString()}>
                        {moment(lastRun.started_at).fromNow()}
                      </TableCell>
                    ))}
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
};
export default AgentFlowList;
