"use client";
import OnboardingButton from "@/components/onboarding/OnboardingButton";
import {
  OnboardingStep,
  OnboardingHeader,
  OnboardingFooter,
} from "@/components/onboarding/OnboardingStep";
import { OnboardingText } from "@/components/onboarding/OnboardingText";
import { useOnboarding } from "../layout";
import { OnboardingGrid } from "@/components/onboarding/OnboardingGrid";
import { useCallback } from "react";
import OnboardingInput from "@/components/onboarding/OnboardingInput";

const services = [
  {
    name: "D-ID",
    text: "Generate AI-powered avatars and videos for dynamic content creation.",
    icon: "/integrations/d-id.png",
  },
  {
    name: "Discord",
    text: "A chat platform for communities and teams, supporting text, voice, and video.",
    icon: "/integrations/discord.png",
  },
  {
    name: "GitHub",
    text: "AutoGPT can track issues, manage repos, and automate workflows with GitHub.",
    icon: "/integrations/github.png",
  },
  {
    name: "Google Workspace",
    text: "Automate emails, calendar events, and document management in AutoGPT with Google Workspace.",
    icon: "/integrations/google.png",
  },
  {
    name: "Google Maps",
    text: "Fetch locations, directions, and real-time geodata for navigation.",
    icon: "/integrations/maps.png",
  },
  {
    name: "HubSpot",
    text: "Manage customer relationships, automate marketing, and track sales.",
    icon: "/integrations/hubspot.png",
  },
  {
    name: "Linear",
    text: "Streamline project management and issue tracking with a modern workflow.",
    icon: "/integrations/linear.png",
  },
  {
    name: "Medium",
    text: "Publish and explore insightful content with a powerful writing platform.",
    icon: "/integrations/medium.png",
  },
  {
    name: "Mem0",
    text: "AI-powered memory assistant for smarter data organization and recall.",
    icon: "/integrations/mem0.png",
  },
  {
    name: "Notion",
    text: "Organize work, notes, and databases in an all-in-one workspace.",
    icon: "/integrations/notion.png",
  },
  {
    name: "NVIDIA",
    text: "Accelerate AI, graphics, and computing with cutting-edge technology.",
    icon: "/integrations/nvidia.jpg",
  },
  {
    name: "OpenWeatherMap",
    text: "Access real-time weather data and forecasts worldwide.",
    icon: "/integrations/openweathermap.png",
  },
  {
    name: "Pinecone",
    text: "Store and search vector data for AI-driven applications.",
    icon: "/integrations/pinecone.png",
  },
  {
    name: "Reddit",
    text: "Explore trending discussions and engage with online communities.",
    icon: "/integrations/reddit.png",
  },
  {
    name: "Slant3D",
    text: "Automate and optimize 3D printing workflows with AI.",
    icon: "/integrations/slant3d.jpeg",
  },
  {
    name: "SMTP",
    text: "Send and manage emails with secure and reliable delivery.",
    icon: "/integrations/smtp.png",
  },
  {
    name: "Todoist",
    text: "Organize tasks and projects with a simple, intuitive to-do list.",
    icon: "/integrations/todoist.png",
  },
  {
    name: "Twitter (X)",
    text: "Stay connected and share updates on the world's biggest conversation platform.",
    icon: "/integrations/x.png",
  },
  {
    name: "Unreal Speech",
    text: "Generate natural-sounding AI voices for speech applications.",
    icon: "/integrations/unreal-speech.png",
  },
];

function isEmptyOrWhitespace(str: string | undefined | null): boolean {
  return !str || str.trim().length === 0;
}

export default function Page() {
  const { state, setState } = useOnboarding(3);

  const switchIntegration = useCallback(
    (name: string) => {
      const integrations = state.integrations.includes(name)
        ? state.integrations.filter((i) => i !== name)
        : [...state.integrations, name];

      setState({ integrations });
    },
    [state.integrations, setState],
  );

  return (
    <OnboardingStep>
      <OnboardingHeader backHref={"/onboarding/2-reason"}>
        <OnboardingText className="mt-4" variant="header" center>
          What platforms or services would you like AutoGPT to work with?
        </OnboardingText>
        <OnboardingText className="mt-1" center>
          You can select more than one option
        </OnboardingText>
      </OnboardingHeader>

      <div className="w-fit">
        <OnboardingText className="my-4" variant="subheader">
          Available integrations
        </OnboardingText>
        <OnboardingGrid
          elements={services}
          selected={state.integrations}
          onSelect={switchIntegration}
        />
        <OnboardingText className="mt-12" variant="subheader">
          Help us grow our integrations
        </OnboardingText>
        <OnboardingText className="my-4">
          Let us know which partnerships you&apos;d like to see next
        </OnboardingText>
        <OnboardingInput
          className="mb-4"
          placeholder="Others (please specify)"
          value={state.otherIntegrations || ""}
          onChange={(otherIntegrations) => setState({ otherIntegrations })}
        />
      </div>

      <OnboardingFooter>
        <OnboardingButton
          className="mb-2"
          href="/onboarding/4-agent"
          disabled={
            state.integrations.length === 0 &&
            isEmptyOrWhitespace(state.otherIntegrations)
          }
        >
          Next
        </OnboardingButton>
      </OnboardingFooter>
    </OnboardingStep>
  );
}
