import React, { useEffect, useRef } from "react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";
import { BlockIORootSchema } from "@/lib/autogpt-server-api/types";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Clipboard } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

export interface BlockOutput {
  id: string;
  hardcodedValues: {
    name: string;
    description: string;
  };
  result?: any;
}

interface OutputModalProps {
  isOpen: boolean;
  onClose: () => void;
  blockOutputs: BlockOutput[];
}

const formatOutput = (output: any): string => {
  if (typeof output === "object") {
    try {
      if (
        Array.isArray(output) &&
        output.every((item) => typeof item === "string")
      ) {
        return output.join("\n").replace(/\\n/g, "\n");
      }
      return JSON.stringify(output, null, 2);
    } catch (error) {
      return `Error formatting output: ${(error as Error).message}`;
    }
  }
  if (typeof output === "string") {
    return output.replace(/\\n/g, "\n");
  }
  return String(output);
};

export function RunnerOutputUI({
  isOpen,
  onClose,
  blockOutputs,
}: OutputModalProps) {
  const { toast } = useToast();

  const copyOutput = (name: string, output: any) => {
    const formattedOutput = formatOutput(output);
    navigator.clipboard.writeText(formattedOutput).then(() => {
      toast({
        title: `"${name}" output copied to clipboard!`,
        duration: 2000,
      });
    });
  };

  const adjustTextareaHeight = (textarea: HTMLTextAreaElement) => {
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  };

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent
        side="right"
        className="flex h-full w-full flex-col overflow-hidden sm:max-w-[600px]"
      >
        <SheetHeader className="px-2 py-2">
          <SheetTitle className="text-xl">Run Outputs</SheetTitle>
          <SheetDescription className="mt-1 text-sm">
            View the outputs from your agent run.
          </SheetDescription>
        </SheetHeader>
        <div className="grow overflow-y-auto px-2 py-2">
          <ScrollArea className="h-full overflow-auto pr-4">
            <div className="space-y-4">
              {blockOutputs && blockOutputs.length > 0 ? (
                blockOutputs.map((block) => (
                  <div key={block.id} className="space-y-1">
                    <Label className="text-base font-semibold">
                      {block.hardcodedValues.name || "Unnamed Output"}
                    </Label>

                    {block.hardcodedValues.description && (
                      <Label className="block text-sm text-gray-600">
                        {block.hardcodedValues.description}
                      </Label>
                    )}

                    <div className="group relative rounded-md bg-gray-100 p-2">
                      <Button
                        className="absolute right-1 top-1 z-10 m-1 hidden p-2 group-hover:block"
                        variant="outline"
                        size="icon"
                        onClick={() =>
                          copyOutput(
                            block.hardcodedValues.name || "Unnamed Output",
                            block.result,
                          )
                        }
                        title="Copy Output"
                      >
                        <Clipboard size={18} />
                      </Button>
                      <Textarea
                        readOnly
                        value={formatOutput(block.result ?? "No output yet")}
                        className="w-full resize-none whitespace-pre-wrap break-words border-none bg-transparent text-sm"
                        style={{
                          height: "auto",
                          minHeight: "2.5rem",
                          maxHeight: "400px",
                        }}
                        ref={(el) => {
                          if (el) {
                            adjustTextareaHeight(el);
                            if (el.scrollHeight > 400) {
                              el.style.height = "400px";
                            }
                          }
                        }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <p>No output blocks available.</p>
              )}
            </div>
          </ScrollArea>
        </div>
      </SheetContent>
    </Sheet>
  );
}

export default RunnerOutputUI;
