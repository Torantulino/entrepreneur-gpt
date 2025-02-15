import { cn } from "@/lib/utils";
import { ReactNode } from "react";

const variants = {
  header: "font-poppin text-xl font-medium leading-7 text-zinc-900",
  subheader: "font-sans text-sm font-medium leading-6 text-zinc-800",
  default: "font-sans text-sm font-normal leading-6 text-zinc-500",
};

export function OnboardingText({
  className,
  center,
  variant = "default",
  children,
}: {
  className?: string;
  center?: boolean;
  variant?: keyof typeof variants;
  children: ReactNode;
}) {
  return (
    <div
      className={cn(
        "w-full",
        center ? "text-center" : "text-left",
        variants[variant] || variants.default,
        className,
      )}
    >
      {children}
    </div>
  );
}
