import { cn } from "@/lib/utils";

interface OnboardingAgentInputProps {
  className?: string;
  name: string;
  description: string;
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
}

export default function OnboardingAgentInput({
  className,
  name,
  description,
  placeholder,
  value,
  onChange,
}: OnboardingAgentInputProps) {
  return (
    <>
      <span className="text=black font-sans text-sm font-medium leading-tight">
        {name}
      </span>
      <span className="text-sm font-normal leading-tight text-slate-500">
        {description}
      </span>
      <input
        className={cn(
          className,
          "relative inline-flex h-11 w-[444px] items-center justify-start rounded-[55px] border border-slate-200 px-4 py-2.5 font-sans text-sm placeholder:text-zinc-400",
          "truncate transition-all duration-200 ease-in-out",
          "focus:border-transparent focus:bg-[#F5F3FF80] focus:outline-none focus:ring-2 focus:ring-violet-700",
        )}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </>
  );
}
