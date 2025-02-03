import React, { useEffect, useState, useCallback } from "react";
import {
  GraphExecution,
  Graph,
  GraphMeta,
  safeCopyGraph,
  BlockUIType,
  BlockIORootSchema,
} from "@/lib/autogpt-server-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button, buttonVariants } from "@/components/ui/button";
import { ClockIcon, ExitIcon, Pencil2Icon } from "@radix-ui/react-icons";
import Link from "next/link";
import { exportAsJSONFile, filterBlocksByType } from "@/lib/utils";
import { FlowRunsStats } from "@/components/monitor/index";
import { Trash2Icon } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { useToast } from "@/components/ui/use-toast";
import { CronScheduler } from "@/components/cronScheduler";
import RunnerInputUI from "@/components/runner-ui/RunnerInputUI";
import useAgentGraph from "@/hooks/useAgentGraph";
import { useBackendAPI } from "@/lib/autogpt-server-api/context";

export const FlowInfo: React.FC<
  React.HTMLAttributes<HTMLDivElement> & {
    flow: GraphMeta;
    executions: GraphExecution[];
    flowVersion?: number | "all";
    refresh: () => void;
  }
> = ({ flow, executions, flowVersion, refresh, ...props }) => {
  const {
    agentName,
    setAgentName,
    agentDescription,
    setAgentDescription,
    savedAgent,
    availableNodes,
    availableFlows,
    getOutputType,
    requestSave,
    requestSaveAndRun,
    requestStopRun,
    scheduleRunner,
    isRunning,
    isScheduling,
    setIsScheduling,
    nodes,
    setNodes,
    edges,
    setEdges,
  } = useAgentGraph(flow.id, flow.version, undefined, false);

  const api = useBackendAPI();
  const { toast } = useToast();

  const [flowVersions, setFlowVersions] = useState<Graph[] | null>(null);
  const [selectedVersion, setSelectedFlowVersion] = useState(
    flowVersion ?? "all",
  );
  const selectedFlowVersion: Graph | undefined = flowVersions?.find(
    (v) =>
      v.version == (selectedVersion == "all" ? flow.version : selectedVersion),
  );

  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [openCron, setOpenCron] = useState(false);
  const [isRunnerInputOpen, setIsRunnerInputOpen] = useState(false);
  const isDisabled = !selectedFlowVersion;

  const getBlockInputsAndOutputs = useCallback(() => {
    const inputBlocks = filterBlocksByType(
      nodes,
      (node) => node.data.uiType === BlockUIType.INPUT,
    );

    const outputBlocks = filterBlocksByType(
      nodes,
      (node) => node.data.uiType === BlockUIType.OUTPUT,
    );

    const inputs = inputBlocks.map((node) => ({
      id: node.id,
      type: "input" as const,
      inputSchema: node.data.inputSchema as BlockIORootSchema,
      hardcodedValues: {
        name: (node.data.hardcodedValues as any).name || "",
        description: (node.data.hardcodedValues as any).description || "",
        value: (node.data.hardcodedValues as any).value,
        placeholder_values:
          (node.data.hardcodedValues as any).placeholder_values || [],
        limit_to_placeholder_values:
          (node.data.hardcodedValues as any).limit_to_placeholder_values ||
          false,
      },
    }));

    const outputs = outputBlocks.map((node) => ({
      id: node.id,
      type: "output" as const,
      hardcodedValues: {
        name: (node.data.hardcodedValues as any).name || "Output",
        description:
          (node.data.hardcodedValues as any).description ||
          "Output from the agent",
        value: (node.data.hardcodedValues as any).value,
      },
      result: (node.data.executionResults as any)?.at(-1)?.data?.output,
    }));

    return { inputs, outputs };
  }, [nodes]);

  const handleScheduleButton = () => {
    if (!selectedFlowVersion) {
      toast({
        title: "Please select a flow version before scheduling",
        duration: 2000,
      });
      return;
    }
    setOpenCron(true);
  };

  useEffect(() => {
    api.getGraphAllVersions(flow.id).then((result) => setFlowVersions(result));
  }, [flow.id, api]);

  const openRunnerInput = () => setIsRunnerInputOpen(true);

  const runOrOpenInput = () => {
    const { inputs } = getBlockInputsAndOutputs();
    if (inputs.length > 0) {
      openRunnerInput();
    } else {
      requestSaveAndRun();
    }
  };

  const handleInputChange = useCallback(
    (nodeId: string, field: string, value: string) => {
      setNodes((nds) =>
        nds.map((node) => {
          if (node.id === nodeId) {
            return {
              ...node,
              data: {
                ...node.data,
                hardcodedValues: {
                  ...(node.data.hardcodedValues as any),
                  [field]: value,
                },
              },
            };
          }
          return node;
        }),
      );
    },
    [setNodes],
  );

  return (
    <Card {...props}>
      <CardHeader className="flex-row justify-between space-x-3 space-y-0">
        <div>
          <CardTitle>
            {flow.name} <span className="font-light">v{flow.version}</span>
          </CardTitle>
        </div>
        <div className="flex items-start space-x-2">
          {(flowVersions?.length ?? 0) > 1 && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">
                  <ClockIcon className="mr-2" />
                  {selectedVersion == "all"
                    ? "All versions"
                    : `Version ${selectedVersion}`}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56">
                <DropdownMenuLabel>Choose a version</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuRadioGroup
                  value={String(selectedVersion)}
                  onValueChange={(choice) =>
                    setSelectedFlowVersion(
                      choice == "all" ? choice : Number(choice),
                    )
                  }
                >
                  <DropdownMenuRadioItem value="all">
                    All versions
                  </DropdownMenuRadioItem>
                  {flowVersions?.map((v) => (
                    <DropdownMenuRadioItem
                      key={v.version}
                      value={v.version.toString()}
                    >
                      Version {v.version}
                      {v.is_active ? " (active)" : ""}
                    </DropdownMenuRadioItem>
                  ))}
                </DropdownMenuRadioGroup>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
          <Link
            className={buttonVariants({ variant: "default" })}
            href={`/build?flowID=${flow.id}&flowVersion=${flow.version}`}
          >
            <Pencil2Icon className="mr-2" />
            Open in Builder
          </Link>
          <Button
            variant="outline"
            className="px-2.5"
            title="Export to a JSON-file"
            data-testid="export-button"
            onClick={async () =>
              exportAsJSONFile(
                safeCopyGraph(
                  flowVersions!.find(
                    (v) => v.version == selectedFlowVersion!.version,
                  )!,
                  await api.getBlocks(),
                ),
                `${flow.name}_v${selectedFlowVersion!.version}.json`,
              )
            }
          >
            <ExitIcon className="mr-2" /> Export
          </Button>
          <Button
            variant="secondary"
            className="bg-purple-500 text-white hover:bg-purple-700"
            onClick={isRunning ? requestStopRun : runOrOpenInput}
            disabled={isDisabled}
            title={!isRunning ? "Run Agent" : "Stop Agent"}
          >
            {isRunning ? "Stop Agent" : "Run Agent"}
          </Button>
          <Button
            variant="outline"
            onClick={() => setIsDeleteModalOpen(true)}
            data-testid="delete-button"
          >
            <Trash2Icon className="h-full" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <FlowRunsStats
          flows={[selectedFlowVersion ?? flow]}
          executions={executions.filter(
            (execution) =>
              execution.graph_id == flow.id &&
              (selectedVersion == "all" ||
                execution.graph_version == selectedVersion),
          )}
        />
      </CardContent>
      <Dialog open={isDeleteModalOpen} onOpenChange={setIsDeleteModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Agent</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this agent? <br />
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsDeleteModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                api.deleteGraph(flow.id).then(() => {
                  setIsDeleteModalOpen(false);
                  refresh();
                });
              }}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <RunnerInputUI
        isOpen={isRunnerInputOpen}
        onClose={() => setIsRunnerInputOpen(false)}
        blockInputs={getBlockInputsAndOutputs().inputs}
        onInputChange={handleInputChange}
        onRun={() => {
          setIsRunnerInputOpen(false);
          requestSaveAndRun();
        }}
        isRunning={isRunning}
        scheduledInput={false}
        isScheduling={false}
        onSchedule={async () => {}} // Fixed type error by making async
      />
    </Card>
  );
};
export default FlowInfo;
