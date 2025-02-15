"use client";
import { ReactNode } from "react";
import OnboardingBackButton from "./OnboardingBackButton";
import { cn } from "@/lib/utils";
import OnboardingProgress from "./OnboardingProgress";
import { useOnboarding } from "@/app/onboarding/layout";

export function OnboardingStep({
  dotted,
  children,
}: {
  dotted?: boolean;
  children: ReactNode;
}) {
  return (
    <div className="relative flex min-h-screen w-full flex-col">
      {dotted && (
        <div className="absolute left-1/2 h-full w-1/2 bg-white bg-[radial-gradient(#e5e7eb77_1px,transparent_1px)] [background-size:10px_10px]"></div>
      )}
      <div className="z-10 flex flex-col items-center">{children}</div>
    </div>
  );
}

interface OnboardingHeaderProps {
  backHref: string;
  transparent?: boolean;
  children?: ReactNode;
}

export function OnboardingHeader({
  backHref,
  transparent,
  children,
}: OnboardingHeaderProps) {
  const { state } = useOnboarding();

  return (
    <div className="sticky top-0 z-10 w-full">
      <div
        className={cn(transparent ? "bg-transparent" : "bg-gray-100", "pb-5")}
      >
        <div className="flex w-full items-center justify-between px-5 py-4">
          <OnboardingBackButton href={backHref} />
          <OnboardingProgress totalSteps={5} toStep={state.step - 1} />
        </div>
        {children}
      </div>

      {!transparent && (
        <div className="h-4 w-full bg-gradient-to-b from-gray-100 via-gray-100/50 to-transparent" />
      )}
    </div>
  );
}

export function OnboardingFooter({ children }: { children?: ReactNode }) {
  return (
    <div className="sticky bottom-0 z-10 w-full">
      <div className="h-4 w-full bg-gradient-to-t from-gray-100 via-gray-100/50 to-transparent" />
      <div className="flex justify-center bg-gray-100">
        <div className="px-5 py-5">{children}</div>
      </div>
    </div>
  );
}
