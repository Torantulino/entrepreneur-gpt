import { cn } from "@/lib/utils";
import Image from "next/image";
import StarRating from "./StarRating";

interface OnboardingAgentCardProps {
  id: string;
  image: string;
  name: string;
  description: string;
  author: string;
  runs: number;
  rating: number;
  selected?: boolean;
  onClick: () => void;
}

export default function OnboardingAgentCard({
  id,
  image,
  name,
  description,
  author,
  runs,
  rating,
  selected,
  onClick,
}: OnboardingAgentCardProps) {
  return (
    <div
      className={cn(
        "relative cursor-pointer transition-all duration-200 ease-in-out",
        "h-[394px] w-[368px] rounded-xl border border-transparent bg-white",
        selected ? "bg-[#F5F3FF80]" : "hover:border-zinc-400",
      )}
      onClick={onClick}
    >
      {/* Image container */}
      <div className="relative">
        <Image
          src={image}
          alt="Agent cover"
          className="m-2 h-[196px] w-[350px] rounded-xl object-cover"
          width={350}
          height={196}
        />
        {/* Profile picture overlay */}
        <div className="absolute bottom-2 left-4">
          <Image
            src={image}
            alt="Profile picture"
            className="h-[50px] w-[50px] rounded-full border border-white object-cover object-center"
            width={50}
            height={50}
          />
        </div>
      </div>

      {/* Content container */}
      <div className="flex h-[180px] flex-col justify-between px-4 pb-3">
        {/* Text content wrapper */}
        <div>
          {/* Title - 2 lines max */}
          <p className="text-md line-clamp-2 max-h-[50px] font-sans text-base font-medium leading-normal text-zinc-800">
            {name}
          </p>

          {/* Author - single line with truncate */}
          <p className="truncate text-sm font-normal leading-normal text-zinc-600">
            by {author}
          </p>

          {/* Description - 3 lines max */}
          <p
            className={cn(
              "mt-2 line-clamp-3 text-sm leading-5",
              selected ? "text-zinc-500" : "text-zinc-400",
            )}
          >
            {description}
          </p>
        </div>

        {/* Bottom stats */}
        <div className="flex w-full items-center justify-between">
          <span className="mt-1 font-sans text-sm font-medium text-zinc-800">
            {runs.toLocaleString("en-US")} runs
          </span>
          <StarRating rating={rating} />
        </div>
      </div>
      <div
        className={cn(
          "pointer-events-none absolute inset-0 rounded-xl border-2 transition-all duration-200 ease-in-out",
          selected ? "border-violet-700" : "border-transparent",
        )}
      />
    </div>
  );
}
