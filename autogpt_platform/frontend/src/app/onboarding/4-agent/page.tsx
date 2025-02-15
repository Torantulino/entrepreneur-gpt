"use client";
import OnboardingButton from "@/components/onboarding/OnboardingButton";
import { useOnboarding } from "../layout";
import {
  OnboardingFooter,
  OnboardingHeader,
  OnboardingStep,
} from "@/components/onboarding/OnboardingStep";
import { OnboardingText } from "@/components/onboarding/OnboardingText";
import OnboardingAgentCard from "@/components/onboarding/OnboardingAgentCard";

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
  const { state, setState } = useOnboarding(4);

  return (
    <OnboardingStep>
      <OnboardingHeader backHref={"/onboarding/3-services"}>
        <OnboardingText className="mt-4" variant="header" center>
          Choose an agent
        </OnboardingText>
        <OnboardingText className="mt-1" center>
          We think these agents are a good match for you based on your answers
        </OnboardingText>
      </OnboardingHeader>

      <div className="my-12 flex items-center justify-between gap-5">
        <OnboardingAgentCard
          {...agents[0]}
          selected={state.chosenAgentId == "0"}
          onClick={() => setState({ chosenAgentId: "0" })}
        />
        <OnboardingAgentCard
          {...agents[1]}
          selected={state.chosenAgentId == "1"}
          onClick={() => setState({ chosenAgentId: "1" })}
        />
      </div>

      <OnboardingFooter>
        <OnboardingButton
          href="/onboarding/5-run"
          disabled={isEmptyOrWhitespace(state.chosenAgentId)}
        >
          Next
        </OnboardingButton>
      </OnboardingFooter>
    </OnboardingStep>
  );
}
