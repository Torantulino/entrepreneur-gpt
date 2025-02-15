import { useState, useEffect, useRef } from "react";

interface OnboardingProgressProps {
  totalSteps: number;
  toStep: number;
}

export default function OnboardingProgress({
  totalSteps,
  toStep,
}: OnboardingProgressProps) {
  const [animatedStep, setAnimatedStep] = useState(toStep - 1);
  const isInitialMount = useRef(true);

  useEffect(() => {
    if (isInitialMount.current) {
      // On initial mount, just set the position without animation
      isInitialMount.current = false;
      return;
    }
    // After initial mount, animate position changes
    setAnimatedStep(toStep - 1);
  }, [toStep]);

  return (
    <div className="relative flex items-center justify-center gap-3">
      {/* Background circles */}
      {Array.from({ length: totalSteps + 1 }).map((_, index) => (
        <div key={index} className="h-2 w-2 rounded-full bg-zinc-400" />
      ))}

      {/* Animated progress indicator */}
      <div
        className={`absolute left-0 h-2 w-7 rounded-full bg-zinc-400 ${
          !isInitialMount.current
            ? "transition-all duration-300 ease-in-out"
            : ""
        }`}
        style={{
          transform: `translateX(${animatedStep * 20}px)`,
        }}
      />
    </div>
  );
}
