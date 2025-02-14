"use client";

import * as React from "react";
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverAnchor,
} from "@/components/ui/popover";
import { PublishAgentSelect } from "../PublishAgentSelect";
import {
  PublishAgentInfo,
  PublishAgentInfoInitialData,
} from "../PublishAgentSelectInfo";
import { PublishAgentAwaitingReview } from "../PublishAgentAwaitingReview";
import { Button } from "../Button";
import {
  StoreSubmissionRequest,
  MyAgentsResponse,
} from "@/lib/autogpt-server-api";
import { useRouter } from "next/navigation";
import { useBackendAPI } from "@/lib/autogpt-server-api/context";
import { useToast } from "@/components/ui/use-toast";
interface PublishAgentPopoutProps {
  trigger?: React.ReactNode;
  openPopout?: boolean;
  inputStep?: "select" | "info" | "review";
  submissionData?: StoreSubmissionRequest;
}

export const PublishAgentPopout: React.FC<PublishAgentPopoutProps> = ({
  trigger,
  openPopout = false,
  inputStep = "select",
  submissionData = {
    name: "",
    sub_heading: "",
    slug: "",
    description: "",
    image_urls: [],
    agent_id: "",
    agent_version: 0,
    categories: [],
  },
}) => {
  const [step, setStep] = React.useState<"select" | "info" | "review">(
    inputStep,
  );
  const [myAgents, setMyAgents] = React.useState<MyAgentsResponse | null>(null);
  const [selectedAgent, setSelectedAgent] = React.useState<string | null>(null);
  const [initialData, setInitialData] =
    React.useState<PublishAgentInfoInitialData>({
      agent_id: "",
      title: "",
      subheader: "",
      slug: "",
      thumbnailSrc: "",
      youtubeLink: "",
      category: "",
      description: "",
    });
  const [publishData, setPublishData] =
    React.useState<StoreSubmissionRequest>(submissionData);
  const [selectedAgentId, setSelectedAgentId] = React.useState<string | null>(
    null,
  );
  const [selectedAgentVersion, setSelectedAgentVersion] = React.useState<
    number | null
  >(null);
  const [open, setOpen] = React.useState(false);

  const popupId = React.useId();
  const router = useRouter();
  const api = useBackendAPI();

  const { toast } = useToast();

  React.useEffect(() => {
    console.log("PublishAgentPopout Effect");
    setOpen(openPopout);
    setStep(inputStep);
    setPublishData(submissionData);
  }, [openPopout]); // eslint-disable-line react-hooks/exhaustive-deps

  React.useEffect(() => {
    console.log("LoadMyAgents Effect");
    if (open) {
      const loadMyAgents = async () => {
        try {
          const response = await api.getMyAgents();
          setMyAgents(response);
        } catch (error) {
          console.error("Failed to load my agents:", error);
        }
      };

      loadMyAgents();
    }
  }, [open, api]);

  const handleClose = () => {
    setStep("select");
    setSelectedAgent(null);
    setPublishData({
      name: "",
      sub_heading: "",
      description: "",
      image_urls: [],
      agent_id: "",
      agent_version: 0,
      slug: "",
      categories: [],
    });
    setOpen(false);
  };

  const handleAgentSelect = (agentName: string) => {
    setSelectedAgent(agentName);
  };

  const handleNextFromSelect = (agentId: string, agentVersion: number) => {
    const selectedAgentData = myAgents?.agents.find(
      (agent) => agent.agent_id === agentId,
    );

    const name = selectedAgentData?.agent_name || "";
    const description = selectedAgentData?.description || "";
    setInitialData({
      agent_id: agentId,
      title: name,
      subheader: "",
      description: description,
      thumbnailSrc: "",
      youtubeLink: "",
      category: "",
      slug: name.replace(/ /g, "-"),
      additionalImages: [],
    });

    setStep("info");
    setSelectedAgentId(agentId);
    setSelectedAgentVersion(agentVersion);
  };

  const handleNextFromInfo = async (
    name: string,
    subHeading: string,
    slug: string,
    description: string,
    imageUrls: string[],
    videoUrl: string,
    categories: string[],
  ) => {
    const missingFields: string[] = [];

    if (!name) missingFields.push("Name");
    if (!subHeading) missingFields.push("Sub-heading");
    if (!description) missingFields.push("Description");
    if (!imageUrls.length) missingFields.push("Image");
    if (!categories.length) missingFields.push("Categories");

    if (missingFields.length > 0) {
      toast({
        title: "Missing Required Fields",
        description: `Please fill in: ${missingFields.join(", ")}`,
        duration: 3000,
      });
      return;
    }

    setPublishData({
      name,
      sub_heading: subHeading,
      description,
      image_urls: imageUrls,
      video_url: videoUrl,
      agent_id: selectedAgentId || "",
      agent_version: selectedAgentVersion || 0,
      slug,
      categories,
    });

    // Create store submission
    try {
      const submission = await api.createStoreSubmission({
        name: name,
        sub_heading: subHeading,
        description: description,
        image_urls: imageUrls,
        video_url: videoUrl,
        agent_id: selectedAgentId || "",
        agent_version: selectedAgentVersion || 0,
        slug: slug.replace(/\s+/g, "-"),
        categories: categories,
      });
      console.log("Store submission created:", submission);
    } catch (error) {
      console.error("Error creating store submission:", error);
    }
    setStep("review");
  };

  const handleBack = () => {
    if (step === "info") {
      setStep("select");
    } else if (step === "review") {
      setStep("info");
    }
  };

  const renderContent = () => {
    switch (step) {
      case "select":
        return (
          <div className="flex min-h-screen items-center justify-center">
            <div className="mx-auto flex w-full max-w-[900px] flex-col rounded-3xl bg-white shadow-lg dark:bg-gray-800">
              <div className="h-full overflow-y-auto">
                <PublishAgentSelect
                  agents={
                    myAgents?.agents.map((agent) => ({
                      name: agent.agent_name,
                      id: agent.agent_id,
                      version: agent.agent_version,
                      lastEdited: agent.last_edited,
                      imageSrc: "https://picsum.photos/300/200", // Fallback image if none provided
                    })) || []
                  }
                  onSelect={handleAgentSelect}
                  onCancel={handleClose}
                  onNext={handleNextFromSelect}
                  onClose={handleClose}
                  onOpenBuilder={() => router.push("/build")}
                />
              </div>
            </div>
          </div>
        );
      case "info":
        return (
          <div className="flex min-h-screen items-center justify-center">
            <div className="mx-auto flex w-full max-w-[900px] flex-col rounded-3xl bg-white shadow-lg dark:bg-gray-800">
              <div className="h-[700px] overflow-y-auto">
                <PublishAgentInfo
                  onBack={handleBack}
                  onSubmit={handleNextFromInfo}
                  onClose={handleClose}
                  initialData={initialData}
                />
              </div>
            </div>
          </div>
        );
      case "review":
        return publishData ? (
          <div className="flex justify-center">
            <div className="mx-auto flex w-full max-w-[900px] flex-col rounded-3xl bg-white shadow-lg dark:bg-gray-800">
              <div className="h-[600px] overflow-y-auto">
                <PublishAgentAwaitingReview
                  agentName={publishData.name}
                  subheader={publishData.sub_heading}
                  description={publishData.description}
                  thumbnailSrc={publishData.image_urls[0]}
                  onClose={handleClose}
                  onDone={handleClose}
                  onViewProgress={() => {
                    router.push("/profile/dashboard");
                    handleClose();
                  }}
                />
              </div>
            </div>
          </div>
        ) : null;
    }
  };

  return (
    <Popover
      open={open}
      onOpenChange={(isOpen) => {
        if (isOpen !== open) {
          setOpen(isOpen);
        }
      }}
    >
      <PopoverTrigger asChild>
        {trigger || <Button>Publish Agent</Button>}
      </PopoverTrigger>
      <PopoverAnchor asChild>
        <div className="fixed left-0 top-0 hidden h-screen w-screen items-center justify-center"></div>
      </PopoverAnchor>

      <PopoverContent
        id={popupId}
        align="center"
        className="z-50 h-screen w-screen bg-transparent"
      >
        {renderContent()}
      </PopoverContent>
    </Popover>
  );
};
