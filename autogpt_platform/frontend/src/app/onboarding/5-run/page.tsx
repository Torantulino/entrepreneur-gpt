"use client";
import OnboardingButton from "@/components/onboarding/OnboardingButton";
import {
  OnboardingStep,
  OnboardingHeader,
} from "@/components/onboarding/OnboardingStep";
import { OnboardingText } from "@/components/onboarding/OnboardingText";
import { useOnboarding } from "../layout";
import StarRating from "@/components/onboarding/StarRating";
import { Play } from "lucide-react";
import { cn } from "@/lib/utils";
import { useCallback, useState } from "react";
import OnboardingAgentInput from "@/components/onboarding/OnboardingAgentInput";
import Image from "next/image";

const agents = [
  {
    id: "0",
    image: "/placeholder.png",
    name: "Viral News Video Creator: AI TikTok Shorts",
    description:
      "Description of what the agent does. Written by the creator. Example of text that's longer than two lines. Lorem ipsum set dolor amet bacon ipsum dolor amet kielbasa chicken ullamco frankfurter cupim nisi. Esse jerky turkey pancetta lorem officia ad qui ut ham hock venison ut pig mollit ball tip. Tempor chicken eiusmod tongue tail pork belly labore kielbasa consequat culpa cow aliqua. Ea tail dolore sausage flank.",
    author: "Pwuts",
    runs: 1539,
    rating: 4.1,
  },
  {
    id: "1",
    image: "/placeholder.png",
    name: "Financial Analysis Agent: Your Personalized Financial Insights Tool",
    description:
      "Description of what the agent does. Written by the creator. Example of text that's longer than two lines. Lorem ipsum set dolor amet bacon ipsum dolor amet kielbasa chicken ullamco frankfurter cupim nisi. Esse jerky turkey pancetta lorem officia ad qui ut ham hock venison ut pig mollit ball tip. Tempor chicken eiusmod tongue tail pork belly labore kielbasa consequat culpa cow aliqua. Ea tail dolore sausage flank.",
    author: "John Ababseh",
    runs: 824,
    rating: 4.5,
  },
];

function isEmptyOrWhitespace(str: string | undefined | null): boolean {
  return !str || str.trim().length === 0;
}

export default function Page() {
  const { state, setState } = useOnboarding(5);
  const [showInput, setShowInput] = useState(false);
  const selectedAgent = agents.find(
    (agent) => agent.id === state.chosenAgentId,
  );

  const setAgentInput = useCallback(
    (key: string, value: string) => {
      setState({
        ...state,
        agentInput: {
          ...state.agentInput,
          [key]: value,
        },
      });
    },
    [state, setState],
  );

  const runYourAgent = (
    <div className="ml-[54px] w-[481px] pl-5">
      <div className="flex flex-col">
        <OnboardingText variant="header">Run your first agent</OnboardingText>
        <span className="mt-9 text-base font-normal leading-normal text-zinc-600">
          A &apos;run&apos; is when your agent starts working on a task
        </span>
        <span className="mt-4 text-base font-normal leading-normal text-zinc-600">
          Click on <b>New Run</b> below to try it out
        </span>

        <div
          onClick={() => {
            setShowInput(true);
            setState({ step: 6 });
          }}
          className={cn(
            "mt-16 flex h-[68px] w-[330px] items-center justify-center rounded-xl border-2 border-violet-700 bg-neutral-50",
            "cursor-pointer transition-all duration-200 ease-in-out hover:bg-violet-50",
          )}
        >
          <svg
            width="38"
            height="38"
            viewBox="0 0 32 32"
            xmlns="http://www.w3.org/2000/svg"
          >
            <g stroke="#6d28d9" strokeWidth="1.2" strokeLinecap="round">
              <line x1="16" y1="8" x2="16" y2="24" />
              <line x1="8" y1="16" x2="24" y2="16" />
            </g>
          </svg>
          <span className="ml-3 font-sans text-[19px] font-medium leading-normal text-violet-700">
            New run
          </span>
        </div>
      </div>
    </div>
  );

  return (
    <OnboardingStep dotted>
      <OnboardingHeader backHref={"/onboarding/4-agent"} transparent />
      <div
        className={cn(
          "flex w-full items-center justify-center",
          showInput ? "mt-[32px]" : "mt-[192px]",
        )}
      >
        {/* Left side */}
        <div className="mr-[52px] w-[481px]">
          <div className="h-[156px] w-[481px] rounded-xl bg-white px-6 pb-5 pt-4">
            <span className="font-sans text-xs font-medium tracking-wide text-zinc-500">
              SELECTED AGENT
            </span>

            <div className="mt-4 flex h-20 rounded-lg bg-violet-50 p-2">
              {/* Left image */}
              <Image
                src="/placeholder.png"
                alt="Description"
                width={350}
                height={196}
                className="h-full w-auto rounded-lg object-contain"
              />

              {/* Right content */}
              <div className="ml-2 flex flex-1 flex-col">
                <span className="w-[292px] truncate font-sans text-[14px] font-medium leading-normal text-zinc-800">
                  {selectedAgent?.name}
                </span>
                <span className="mt-[5px] w-[292px] truncate font-sans text-xs font-normal leading-tight text-zinc-600">
                  by {selectedAgent?.author}
                </span>
                <div className="mt-auto flex w-[292px] justify-between">
                  <span className="mt-1 truncate font-sans text-xs font-normal leading-tight text-zinc-600">
                    {selectedAgent?.runs.toLocaleString("en-US")} runs
                  </span>
                  <StarRating
                    className="font-sans text-xs font-normal leading-tight text-zinc-600"
                    starSize={12}
                    rating={selectedAgent?.rating || 0}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right side */}
        {!showInput ? (
          runYourAgent
        ) : (
          <div className="ml-[54px] w-[481px] pl-5">
            <div className="flex flex-col">
              <OnboardingText variant="header">
                Provide details for your agent
              </OnboardingText>
              <span className="mt-9 text-base font-normal leading-normal text-zinc-600">
                Give your agent the details it needs to work—just enter <br />
                the key information and get started.
              </span>
              <span className="mt-4 text-base font-normal leading-normal text-zinc-600">
                When you&apos;re done, click <b>Run Agent</b>.
              </span>
              <div className="mt-12 inline-flex w-[492px] flex-col items-start justify-start gap-2 rounded-[20px] border border-zinc-300 bg-white p-6">
                <OnboardingText className="mb-3 font-semibold" variant="header">
                  Input
                </OnboardingText>
                <OnboardingAgentInput
                  name={"Video Count"}
                  description={"The number of videos you'd like to generate"}
                  placeholder={"eg. 1"}
                  value={state.agentInput?.videoCount || ""}
                  onChange={(v) => setAgentInput("videoCount", v)}
                />
                <OnboardingAgentInput
                  name={"Source Website"}
                  description={"The website to source the stories from"}
                  placeholder={"eg. youtube URL"}
                  value={state.agentInput?.sourceWebsite || ""}
                  onChange={(v) => setAgentInput("sourceWebsite", v)}
                />
              </div>
              <OnboardingButton
                variant="violet"
                className="mt-8 w-[136px]"
                disabled={
                  isEmptyOrWhitespace(state.agentInput?.videoCount) ||
                  isEmptyOrWhitespace(state.agentInput?.sourceWebsite)
                }
              >
                <Play className="" size={18} />
                Run agent
              </OnboardingButton>
            </div>
          </div>
        )}
      </div>
    </OnboardingStep>
  );
}
