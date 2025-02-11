import Image from "next/image";
import { StarRatingIcons } from "@/components/ui/icons";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useState } from "react";
import { StoreAgent } from "@/lib/autogpt-server-api";

interface FeaturedStoreCardProps {
  agent: StoreAgent;
  backgroundColor: string;
}

export const FeaturedAgentCard: React.FC<FeaturedStoreCardProps> = ({
  agent,
  backgroundColor,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <Card
      data-testid="featured-store-card"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={backgroundColor}
    >
      <CardHeader>
        <CardTitle>{agent.agent_name}</CardTitle>
        <CardDescription>{agent.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="relative h-[397px] w-full overflow-hidden rounded-xl">
          <div
            className={`transition-opacity duration-200 ${isHovered ? "opacity-0" : "opacity-100"}`}
          >
            <Image
              src={agent.agent_image || "/AUTOgpt_Logo_dark.png"}
              alt={`${agent.agent_name} preview`}
              fill
              sizes="100%"
              className="rounded-xl object-cover"
            />
          </div>
          <div
            className={`absolute inset-0 overflow-y-auto transition-opacity duration-200 ${
              isHovered ? "opacity-100" : "opacity-0"
            } rounded-xl dark:bg-neutral-700`}
          >
            <p className="text-base text-neutral-800 dark:text-neutral-200">
              {agent.description}
            </p>
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex items-center justify-between">
        <div className="font-semibold">
          {agent.runs?.toLocaleString() ?? "0"} runs
        </div>
        <div className="flex items-center gap-1.5">
          <p>{agent.rating.toFixed(1) ?? "0.0"}</p>
          <div
            className="inline-flex items-center justify-start gap-px"
            role="img"
            aria-label={`Rating: ${agent.rating.toFixed(1)} out of 5 stars`}
          >
            {StarRatingIcons(agent.rating)}
          </div>
        </div>
      </CardFooter>
    </Card>
  );
};
