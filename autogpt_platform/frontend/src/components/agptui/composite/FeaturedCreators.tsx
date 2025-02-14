"use client";

import * as React from "react";
import { CreatorCard } from "@/components/agptui/CreatorCard";
import { useRouter } from "next/navigation";

export interface FeaturedCreator {
  name: string;
  username: string;
  description: string;
  avatar_url: string;
  num_agents: number;
}

interface FeaturedCreatorsProps {
  title?: string;
  featuredCreators: FeaturedCreator[];
}

export const FeaturedCreators: React.FC<FeaturedCreatorsProps> = ({
  featuredCreators,
  title = "Featured Creators",
}) => {
  const router = useRouter();

  const handleCardClick = (creator: string) => {
    router.push(`/marketplace/creator/${encodeURIComponent(creator)}`);
  };

  // Only show first 4 creators
  const displayedCreators = featuredCreators.slice(0, 4);

  return (
    <div className="flex w-full flex-col items-center justify-center py-16">
      <div className="w-full max-w-[1360px]">
        <h2 className="mb-8 font-poppins text-2xl font-semibold leading-7 text-neutral-800 dark:text-neutral-200">
          {title}
        </h2>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
          {displayedCreators.map((creator, index) => (
            <CreatorCard
              key={index}
              creatorName={creator.name || creator.username}
              creatorImage={creator.avatar_url}
              bio={creator.description}
              agentsUploaded={creator.num_agents}
              onClick={() => handleCardClick(creator.username)}
              index={index}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
