import React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { BlockIORootSchema } from "@/lib/autogpt-server-api/types";
import { InputList } from "./RunnerInputList";

export interface BlockInput {
  id: string;
  inputSchema: BlockIORootSchema;
  hardcodedValues: {
    name: string;
    description: string;
    value: any;
    placeholder_values?: any[];
    limit_to_placeholder_values?: boolean;
  };
}

interface RunSettingsUiProps {
  isOpen: boolean;
  onClose: () => void;
  blockInputs: BlockInput[];
  onInputChange: (nodeId: string, field: string, value: string) => void;
  onRun: () => void;
  onSchedule: () => Promise<void>;
  scheduledInput: boolean;
  isScheduling: boolean;
  isRunning: boolean;
}

export function RunnerInputUI({
  isOpen,
  onClose,
  blockInputs,
  isScheduling,
  onInputChange,
  onRun,
  onSchedule,
  scheduledInput,
  isRunning,
}: RunSettingsUiProps) {
  const handleRun = () => {
    onRun();
    onClose();
  };

  const handleSchedule = async () => {
    onClose();
    await onSchedule();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="flex max-h-[80vh] flex-col overflow-hidden sm:max-w-[400px] md:max-w-[500px] lg:max-w-[600px]">
        <DialogHeader className="px-4 py-4">
          <DialogTitle className="text-2xl">
            {scheduledInput ? "Schedule Settings" : "Run Settings"}
          </DialogTitle>
          <DialogDescription className="mt-2 text-sm">
            Configure settings for running your agent.
          </DialogDescription>
        </DialogHeader>
        <div className="grow overflow-y-auto px-4 py-4">
          <InputList blockInputs={blockInputs} onInputChange={onInputChange} />
        </div>
        <DialogFooter className="px-6 py-4">
          <Button
            data-testid="run-dialog-run-button"
            onClick={scheduledInput ? handleSchedule : handleRun}
            className="px-8 py-2 text-lg"
            disabled={scheduledInput ? isScheduling : isRunning}
          >
            {scheduledInput ? "Schedule" : isRunning ? "Running..." : "Run"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default RunnerInputUI;
