import { cn } from "@/lib/utils";

interface OnboardingInputProps {
  className?: string;
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
}

export default function OnboardingInput({
  className,
  placeholder,
  value,
  onChange,
}: OnboardingInputProps) {
  return (
    <input
      className={cn(
        className,
        "relative h-[50px] w-[512px] rounded-[25px] border border-transparent bg-white px-4 font-poppin text-sm font-normal leading-normal text-zinc-900 placeholder:text-zinc-400",
        "transition-all duration-200 ease-in-out",
        "focus:border-transparent focus:bg-[#F5F3FF80] focus:outline-none focus:ring-2 focus:ring-violet-700",
      )}
      placeholder={placeholder}
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  );
}
