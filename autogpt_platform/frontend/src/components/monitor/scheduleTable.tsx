import { Schedule } from "@/lib/autogpt-server-api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ClockIcon, Loader2 } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { CronExpressionManager } from "@/lib/monitor/cronExpressionManager";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { GraphMeta } from "@/lib/autogpt-server-api";
import { useRouter } from "next/navigation";
import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { TextRenderer } from "../ui/render";
import { Input } from "../ui/input";
import { Label } from "../ui/label";

interface SchedulesTableProps {
  schedules: Schedule[];
  agents: GraphMeta[];
  onRemoveSchedule: (scheduleId: string, enabled: boolean) => void;
  sortColumn: keyof Schedule;
  sortDirection: "asc" | "desc";
  onSort: (column: keyof Schedule) => void;
}

export const SchedulesTable = ({
  schedules,
  agents,
  onRemoveSchedule,
  sortColumn,
  sortDirection,
  onSort,
}: SchedulesTableProps) => {
  const { toast } = useToast();
  const router = useRouter();
  const cron_manager = new CronExpressionManager();
  const [selectedAgent, setSelectedAgent] = useState<string>("");
  const [selectedVersion, setSelectedVersion] = useState<number>(0);
  const [maxVersion, setMaxVersion] = useState<number>(0);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState<string>("");

  const filteredAndSortedSchedules = [...schedules]
    .filter(
      (schedule) => !selectedFilter || schedule.graph_id === selectedFilter,
    )
    .sort((a, b) => {
      const aValue = a[sortColumn];
      const bValue = b[sortColumn];
      if (sortDirection === "asc") {
        return String(aValue).localeCompare(String(bValue));
      }
      return String(bValue).localeCompare(String(aValue));
    });

  const handleToggleSchedule = (scheduleId: string, enabled: boolean) => {
    onRemoveSchedule(scheduleId, enabled);
    if (!enabled) {
      toast({
        title: "Schedule Disabled",
        description: "The schedule has been successfully disabled.",
      });
    }
  };

  const handleNewSchedule = () => {
    setIsDialogOpen(true);
  };

  const handleAgentSelect = (agentId: string) => {
    setSelectedAgent(agentId);
    const agent = agents.find((a) => a.id === agentId);
    setMaxVersion(agent!.version);
    setSelectedVersion(agent!.version);
  };

  const handleVersionSelect = (version: string) => {
    setSelectedVersion(parseInt(version));
  };

  const handleSchedule = async () => {
    if (!selectedAgent || !selectedVersion) {
      toast({
        title: "Invalid Input",
        description: "Please select an agent and a version.",
        variant: "destructive",
      });
      return;
    }
    if (selectedVersion < 1 || selectedVersion > maxVersion) {
      toast({
        title: "Invalid Version",
        description: `Please select a version between 1 and ${maxVersion}.`,
        variant: "destructive",
      });
      return;
    }
    setIsLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 100));
      router.push(
        `/build?flowID=${selectedAgent}&flowVersion=${selectedVersion}&open_scheduling=true`,
      );
    } catch (error) {
      console.error("Navigation error:", error);
    }
  };

  return (
    <Card className="h-fit p-4">
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Select Agent for New Schedule</DialogTitle>
          </DialogHeader>
          <Select onValueChange={handleAgentSelect}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select an agent" />
            </SelectTrigger>
            <SelectContent>
              {agents.map((agent, i) => (
                <SelectItem key={agent.id + i} value={agent.id}>
                  <TextRenderer value={agent.name} truncateLengthLimit={30} />
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Label className="mt-4">
            Select version between 1 and {maxVersion}
          </Label>
          <Input
            type="number"
            min={1}
            max={selectedAgent ? maxVersion : 0}
            value={selectedVersion}
            onChange={(e) => handleVersionSelect(e.target.value)}
            placeholder="Select version"
            className="w-full"
          />
          <Button
            onClick={handleSchedule}
            disabled={isLoading || !selectedAgent}
            className="mt-4"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Loading...
              </>
            ) : (
              "Schedule"
            )}
          </Button>
        </DialogContent>
      </Dialog>

      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold">Schedules</h3>
        <div className="flex gap-2">
          <Select onValueChange={setSelectedFilter}>
            <SelectTrigger className="h-8 w-[180px] rounded-md px-3 text-xs">
              <SelectValue placeholder="Filter by graph" />
            </SelectTrigger>
            <SelectContent className="text-xs">
              {agents.map((agent) => (
                <SelectItem key={agent.id} value={agent.id}>
                  {agent.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button size="sm" variant="outline" onClick={handleNewSchedule}>
            <ClockIcon className="mr-2 h-4 w-4" />
            New Schedule
          </Button>
        </div>
      </div>
      <ScrollArea className="max-h-[400px]">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead
                onClick={() => onSort("graph_id")}
                className="cursor-pointer"
              >
                Graph Name
              </TableHead>
              <TableHead className="cursor-pointer">Graph Version</TableHead>
              <TableHead
                onClick={() => onSort("next_run_time")}
                className="cursor-pointer"
              >
                Next Execution
              </TableHead>
              <TableHead
                onClick={() => onSort("cron")}
                className="cursor-pointer"
              >
                Schedule
              </TableHead>

              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredAndSortedSchedules.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={4}
                  className="py-8 text-center text-lg text-gray-400"
                >
                  No schedules are available
                </TableCell>
              </TableRow>
            ) : (
              filteredAndSortedSchedules.map((schedule) => (
                <TableRow key={schedule.id}>
                  <TableCell className="font-medium">
                    {agents.find((a) => a.id === schedule.graph_id)?.name ||
                      schedule.graph_id}
                  </TableCell>
                  <TableCell>{schedule.graph_version}</TableCell>
                  <TableCell>
                    {new Date(schedule.next_run_time).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary">
                      {cron_manager.generateDescription(schedule.cron || "")}
                    </Badge>
                  </TableCell>

                  <TableCell>
                    <div className="flex space-x-2">
                      <Button
                        variant={"destructive"}
                        onClick={() => handleToggleSchedule(schedule.id, false)}
                      >
                        Remove
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </ScrollArea>
    </Card>
  );
};
