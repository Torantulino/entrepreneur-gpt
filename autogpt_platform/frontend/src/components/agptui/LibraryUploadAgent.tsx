"use client";
import { Upload, X } from "lucide-react";
import { Button } from "./Button";
import { useState } from "react";
import { motion, useAnimation } from "framer-motion";
import { cn, removeCredentials } from "@/lib/utils";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "../ui/input";
import { FileUploader } from "react-drag-drop-files";
import { Graph, GraphCreatable } from "@/lib/autogpt-server-api";
import { useBackendAPI } from "@/lib/autogpt-server-api/context";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/components/ui/use-toast";

const fileTypes = ["JSON"];

const fileSchema = z.custom<File>((val) => val instanceof File, {
  message: "Must be a File object",
});

const formSchema = z.object({
  agentFile: fileSchema,
  agentName: z.string().min(1, "Agent name is required"),
  agentDescription: z.string(),
});

function updateBlockIDs(graph: Graph) {
  const updatedBlockIDMap: Record<string, string> = {
    "a1b2c3d4-5e6f-7g8h-9i0j-k1l2m3n4o5p6":
      "436c3984-57fd-4b85-8e9a-459b356883bd",
    "b2g2c3d4-5e6f-7g8h-9i0j-k1l2m3n4o5p6":
      "0e50422c-6dee-4145-83d6-3a5a392f65de",
    "c3d4e5f6-7g8h-9i0j-1k2l-m3n4o5p6q7r8":
      "a0a69be1-4528-491c-a85a-a4ab6873e3f0",
    "c3d4e5f6-g7h8-i9j0-k1l2-m3n4o5p6q7r8":
      "32a87eab-381e-4dd4-bdb8-4c47151be35a",
    "b2c3d4e5-6f7g-8h9i-0j1k-l2m3n4o5p6q7":
      "87840993-2053-44b7-8da4-187ad4ee518c",
    "h1i2j3k4-5l6m-7n8o-9p0q-r1s2t3u4v5w6":
      "d0822ab5-9f8a-44a3-8971-531dd0178b6b",
    "d3f4g5h6-1i2j-3k4l-5m6n-7o8p9q0r1s2t":
      "df06086a-d5ac-4abb-9996-2ad0acb2eff7",
    "h5e7f8g9-1b2c-3d4e-5f6g-7h8i9j0k1l2m":
      "f5b0f5d0-1862-4d61-94be-3ad0fa772760",
    "a1234567-89ab-cdef-0123-456789abcdef":
      "4335878a-394e-4e67-adf2-919877ff49ae",
    "f8e7d6c5-b4a3-2c1d-0e9f-8g7h6i5j4k3l":
      "f66a3543-28d3-4ab5-8945-9b336371e2ce",
    "b29c1b50-5d0e-4d9f-8f9d-1b0e6fcbf0h2":
      "716a67b3-6760-42e7-86dc-18645c6e00fc",
    "31d1064e-7446-4693-o7d4-65e5ca9110d1":
      "cc10ff7b-7753-4ff2-9af6-9399b1a7eddc",
    "c6731acb-4105-4zp1-bc9b-03d0036h370g":
      "5ebe6768-8e5d-41e3-9134-1c7bd89a8d52",
  };
  graph.nodes
    .filter((node) => node.block_id in updatedBlockIDMap)
    .forEach((node) => {
      node.block_id = updatedBlockIDMap[node.block_id];
    });
  return graph;
}

export const LibraryUploadAgent = () => {
  const [isDroped, setisDroped] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const controls = useAnimation();
  const api = useBackendAPI();
  const { toast } = useToast();
  const [agentObject, setAgentObject] = useState<GraphCreatable | null>(null);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      agentName: "",
      agentDescription: "",
    },
  });

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    if (!agentObject) {
      form.setError("root", { message: "No Agent object to save" });
      return;
    }

    setIsLoading(true);

    const payload: GraphCreatable = {
      ...agentObject,
      name: values.agentName,
      description: values.agentDescription,
      is_active: true,
    };

    try {
      const response = await api.createGraph(payload);
      setIsOpen(false);
      toast({
        title: "Success",
        description: "Agent uploaded successfully",
        variant: "default",
      });
      const qID = "flowID";
      window.location.href = `/build?${qID}=${response.id}`;
    } catch (error) {
      form.setError("root", {
        message: `Could not create agent: ${error}`,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (file: File) => {
    setTimeout(() => {
      setisDroped(false);
    }, 2000);

    form.setValue("agentFile", file);
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const obj = JSON.parse(event.target?.result as string);
        if (
          !["name", "description", "nodes", "links"].every(
            (key) => key in obj && obj[key] != null,
          )
        ) {
          throw new Error(
            "Invalid agent object in file: " + JSON.stringify(obj, null, 2),
          );
        }
        const agent = obj as Graph;
        removeCredentials(agent);
        updateBlockIDs(agent);
        setAgentObject(agent);
        if (!form.getValues("agentName")) {
          form.setValue("agentName", agent.name);
        }
        if (!form.getValues("agentDescription")) {
          form.setValue("agentDescription", agent.description);
        }
      } catch (error) {
        console.error("Error loading agent file:", error);
      }
    };
    reader.readAsText(file);
    setisDroped(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button
          variant="library_primary"
          size="library"
          className="w-fit sm:w-[177px]"
        >
          <Upload className="h-5 w-5 sm:mr-2" />
          <span className="hidden items-center sm:inline-flex">
            Upload an agent
          </span>
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="mb-8 text-center">Upload Agent</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="agentName"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Agent name</FormLabel>
                  <FormControl>
                    <Input {...field} className="w-full rounded-[10px]" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="agentDescription"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea {...field} className="w-full rounded-[10px]" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="agentFile"
              render={({ field }) => (
                <FormItem className="rounded-xl border-2 border-dashed border-neutral-300 hover:border-neutral-600">
                  <FormControl>
                    {field.value ? (
                      <div className="relative flex rounded-[10px] border p-2 font-sans text-sm font-medium text-[#525252] outline-none">
                        <span className="line-clamp-1">{field.value.name}</span>
                        <Button
                          onClick={() =>
                            form.setValue("agentFile", undefined as any)
                          }
                          className="absolute left-[-10px] top-[-16px] mt-2 h-fit border-none bg-red-200 p-1"
                          size="library"
                        >
                          <X
                            className="m-0 h-[12px] w-[12px] text-red-600"
                            strokeWidth={3}
                          />
                        </Button>
                      </div>
                    ) : (
                      <FileUploader
                        handleChange={handleChange}
                        name="file"
                        types={fileTypes}
                        label={"Upload your agent here..!!"}
                        uploadedLabel={"Uploading Successful"}
                        required={true}
                        hoverTitle={"Drop your agent here...!!"}
                        maxSize={10}
                        classes={"drop-style"}
                        onDrop={() => {
                          setisDroped(true);
                        }}
                        onSelect={() => setisDroped(true)}
                      >
                        <div
                          style={{
                            minHeight: "150px",
                            display: "flex",
                            flexDirection: "column",
                            justifyContent: "center",
                            alignItems: "center",
                            outline: "none",
                            fontFamily: "var(--font-geist-sans)",
                            color: "#525252",
                            fontSize: "14px",
                            fontWeight: "500",
                            borderWidth: "0px",
                          }}
                        >
                          {isDroped ? (
                            <div className="flex items-center justify-center py-4">
                              <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-t-2 border-neutral-800"></div>
                            </div>
                          ) : (
                            <>
                              <span>Drop your agent here</span>
                              <span>or</span>
                              <span>Click to upload</span>
                            </>
                          )}
                        </div>
                      </FileUploader>
                    )}
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button
              type="submit"
              variant="library_primary"
              size="library"
              className="mt-2 self-end"
              disabled={!agentObject || isLoading}
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="h-4 w-4 animate-spin rounded-full border-b-2 border-t-2 border-white"></div>
                  <span>Uploading...</span>
                </div>
              ) : (
                "Upload Agent"
              )}
            </Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};
