import React, { FC } from "react";
import { Button } from "./ui/button";
import { NodeExecutionResult } from "@/lib/autogpt-server-api/types";
import DataTable from "./DataTable";
import { Separator } from "@/components/ui/separator";

interface OutputModalProps {
  isOpen: boolean;
  onClose: () => void;
  executionResults: {
    execId: string;
    data: NodeExecutionResult["output_data"];
  }[];
}

const OutputModalComponent: FC<OutputModalProps> = ({
  isOpen,
  onClose,
  executionResults,
}) => {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="nodrag nowheel fixed inset-0 flex items-center justify-center bg-white bg-opacity-60">
      <div className="w-[500px] max-w-[90%] rounded-lg border-[1.5px] bg-white p-5">
        <strong>Output Data History</strong>
        <div className="my-2 max-h-[384px] grow overflow-y-auto rounded-md p-2">
          {executionResults.map((data, i) => (
            <>
              <DataTable key={i} title={data.execId} data={data.data} />
              <Separator />
            </>
          ))}
        </div>
        <div className="mt-2.5 flex justify-end gap-2.5">
          <Button onClick={onClose}>Close</Button>
        </div>
      </div>
    </div>
  );
};

export default OutputModalComponent;
