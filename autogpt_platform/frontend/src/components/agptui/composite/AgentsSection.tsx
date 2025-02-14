"use client";

import * as React from "react";
import { StoreCard } from "@/components/agptui/StoreCard";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
} from "@/components/ui/carousel";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";

export interface Agent {
  slug: string;
  agent_name: string;
  agent_image: string;
  creator: string;
  creator_avatar: string;
  sub_heading: string;
  description: string;
  runs: number;
  rating: number;
}

interface AgentsSectionProps {
  sectionTitle: string;
  agents: Agent[];
  hideAvatars?: boolean;
}

export const AgentsSection: React.FC<AgentsSectionProps> = ({
  sectionTitle,
  agents: allAgents,
  hideAvatars = false,
}) => {
  const router = useRouter();

  // TODO: Update this when we have pagination
  const displayedAgents = allAgents;

  const handleCardClick = (creator: string, slug: string) => {
    router.push(
      `/marketplace/agent/${encodeURIComponent(creator)}/${encodeURIComponent(slug)}`,
    );
  };

  return (
    <div className="flex flex-col items-center justify-center py-4 lg:py-8">
      <div className="w-full max-w-[1360px]">
        <div className="decoration-skip-ink-none mb-8 text-left font-poppins text-[18px] font-[600] leading-7 text-[#282828] underline-offset-[from-font] dark:text-neutral-200">
          {sectionTitle}
        </div>
        {!displayedAgents || displayedAgents.length === 0 ? (
          <div className="text-center text-gray-500 dark:text-gray-400">
            No agents found
          </div>
        ) : (
          <>
            {/* Mobile Carousel View */}
            <Carousel
              className="md:hidden"
              opts={{
                loop: true,
              }}
            >
              <CarouselContent>
                {displayedAgents.map((agent, index) => (
                  <CarouselItem key={index} className="min-w-64 max-w-71">
                    <StoreCard
                      agentName={agent.agent_name}
                      agentImage={agent.agent_image}
                      description={agent.description}
                      runs={agent.runs}
                      rating={agent.rating}
                      avatarSrc={agent.creator_avatar}
                      creatorName={agent.creator}
                      hideAvatar={hideAvatars}
                      onClick={() => handleCardClick(agent.creator, agent.slug)}
                    />
                  </CarouselItem>
                ))}
              </CarouselContent>
            </Carousel>

            <div className="hidden grid-cols-1 place-items-center gap-6 md:grid md:grid-cols-2 lg:grid-cols-4">
              {displayedAgents.map((agent, index) => (
                <StoreCard
                  key={index}
                  agentName={agent.agent_name}
                  agentImage={agent.agent_image}
                  description={agent.description}
                  runs={agent.runs}
                  rating={agent.rating}
                  avatarSrc={agent.creator_avatar}
                  creatorName={agent.creator}
                  hideAvatar={hideAvatars}
                  onClick={() => handleCardClick(agent.creator, agent.slug)}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};
