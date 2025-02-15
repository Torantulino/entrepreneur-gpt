import { cn } from "@/lib/utils";
import Image from "next/image";

type OnboardingGridElementProps = {
  name: string;
  text: string;
  icon: string;
  selected: boolean;
  onClick: () => void;
};

function OnboardingGridElement({
  name,
  text,
  icon,
  selected,
  onClick,
}: OnboardingGridElementProps) {
  return (
    <button
      className={cn(
        "relative flex h-[236px] w-[200px] flex-col items-start gap-2 rounded-xl border border-transparent bg-white p-[15px] font-sans",
        "transition-all duration-200 ease-in-out",
        selected ? "bg-[#F5F3FF80]" : "hover:border-zinc-400",
      )}
      onClick={onClick}
    >
      <Image
        src={icon}
        alt={`Logo of ${name}`}
        className="h-12 w-12 rounded-lg object-contain object-center"
        width={48}
        height={48}
      />
      <span className="text-md mt-4 w-full text-left font-medium leading-normal text-[#121212]">
        {name}
      </span>
      <span className="w-full text-left text-[11.5px] font-normal leading-5 text-zinc-500">
        {text}
      </span>
      <div
        className={cn(
          "pointer-events-none absolute inset-0 rounded-xl border-2 transition-all duration-200 ease-in-out",
          selected ? "border-violet-700" : "border-transparent",
        )}
      />
    </button>
  );
}

type OnboardingGridProps = {
  className?: string;
  elements: Array<{
    name: string;
    text: string;
    icon: string;
  }>;
  selected?: string[];
  onSelect: (name: string) => void;
};

export function OnboardingGrid({
  className,
  elements,
  selected,
  onSelect,
}: OnboardingGridProps) {
  return (
    <div
      className={cn(
        className,
        "grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4",
      )}
    >
      {elements.map((element) => (
        <OnboardingGridElement
          key={element.name}
          name={element.name}
          text={element.text}
          icon={element.icon}
          selected={selected?.includes(element.name) || false}
          onClick={() => onSelect(element.name)}
        />
      ))}
    </div>
  );
}
