"use client";
import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useState,
} from "react";

type OnboardingState = {
  step: number;
  usageReason?: string;
  integrations: string[];
  otherIntegrations?: string;
  chosenAgentId?: string;
  agentInput?: { [key: string]: string };
};

const OnboardingContext = createContext<
  | {
      state: OnboardingState;
      setState: (state: Partial<OnboardingState>) => void;
    }
  | undefined
>(undefined);

export function useOnboarding(step?: number) {
  const context = useContext(OnboardingContext);
  if (!context)
    throw new Error("useOnboarding must be used within OnboardingLayout");

  useEffect(() => {
    if (!step) return;

    context.setState({ step });
  }, [step]);

  return context;
}

export default function OnboardingLayout({
  children,
}: {
  children: ReactNode;
}) {
  const [state, setStateRaw] = useState<OnboardingState>({
    step: 0,
    integrations: [],
  });

  const setState = (newState: Partial<OnboardingState>) => {
    setStateRaw((prev) => ({ ...prev, ...newState }));
  };

  return (
    <OnboardingContext.Provider value={{ state, setState }}>
      <div className="flex min-h-screen w-full items-center justify-center bg-gray-100">
        <div className="mx-auto flex w-full flex-col items-center">
          {children}
        </div>
      </div>
    </OnboardingContext.Provider>
  );
}
