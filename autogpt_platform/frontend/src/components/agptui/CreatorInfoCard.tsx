import * as React from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { StarRatingIcons } from "@/components/ui/icons";

interface CreatorInfoCardProps {
  username: string;
  handle: string;
  avatarSrc: string;
  categories: string[];
  averageRating: number;
  totalRuns: number;
}

export const CreatorInfoCard: React.FC<CreatorInfoCardProps> = ({
  username,
  handle,
  avatarSrc,
  categories,
  averageRating,
  totalRuns,
}) => {
  return (
    <div
      className="inline-flex h-auto min-h-[500px] w-full max-w-[440px] flex-col items-start justify-between rounded-[26px] bg-violet-100 p-4 dark:bg-violet-900 sm:h-[632px] sm:w-[440px] sm:p-6"
      role="article"
      aria-label={`Creator profile for ${username}`}
    >
      <div className="flex w-full flex-col items-start justify-start gap-3.5 sm:h-[218px]">
        <Avatar className="h-[100px] w-[100px] sm:h-[130px] sm:w-[130px]">
          <AvatarImage src={avatarSrc} alt={`${username}'s avatar`} />
          <AvatarFallback className="h-[100px] w-[100px] sm:h-[130px] sm:w-[130px]">
            {username.charAt(0)}
          </AvatarFallback>
        </Avatar>
        <div className="flex w-full flex-col items-start justify-start gap-1.5">
          <div className="w-full font-poppins text-[35px] font-medium leading-10 text-neutral-900 dark:text-neutral-100 sm:text-[35px] sm:leading-10">
            {username}
          </div>
          <div className="font-geist w-full text-lg font-normal leading-6 text-neutral-800 dark:text-neutral-200 sm:text-xl sm:leading-7">
            @{handle}
          </div>
        </div>
      </div>

      <div className="my-4 flex w-full flex-col items-start justify-start gap-6 sm:gap-[50px]">
        <div className="flex w-full flex-col items-start justify-start gap-3">
          <div className="h-px w-full bg-neutral-700 dark:bg-neutral-300" />
          <div className="flex flex-col items-start justify-start gap-2.5">
            <div className="w-full font-neue text-base font-medium leading-normal text-neutral-800 dark:text-neutral-200">
              Top categories
            </div>
            <div
              className="flex flex-wrap items-center gap-2.5"
              role="list"
              aria-label="Categories"
            >
              {categories.map((category, index) => (
                <div
                  key={index}
                  className="flex items-center justify-center gap-2.5 rounded-[34px] border border-neutral-600 px-4 py-3 dark:border-neutral-400"
                  role="listitem"
                >
                  <div className="font-neue text-base font-normal leading-normal text-neutral-800 dark:text-neutral-200">
                    {category}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="flex w-full flex-col items-start justify-start gap-3">
          <div className="h-px w-full bg-neutral-700 dark:bg-neutral-300" />
          <div className="flex w-full flex-col items-start justify-between gap-4 sm:flex-row sm:gap-0">
            <div className="flex w-full flex-col items-start justify-start gap-2.5 sm:w-[164px]">
              <div className="w-full font-neue text-base font-medium leading-normal text-neutral-800 dark:text-neutral-200">
                Average rating
              </div>
              <div className="inline-flex items-center gap-2">
                <div className="font-geist text-[18px] font-semibold leading-[28px] text-neutral-800 dark:text-neutral-200">
                  {averageRating.toFixed(1)}
                </div>
                <div
                  className="flex items-center gap-px"
                  role="img"
                  aria-label={`Rating: ${averageRating} out of 5 stars`}
                >
                  {StarRatingIcons(averageRating)}
                </div>
              </div>
            </div>
            <div className="flex w-full flex-col items-start justify-start gap-2.5 sm:w-[164px]">
              <div className="w-full font-neue text-base font-medium leading-normal text-neutral-800 dark:text-neutral-200">
                Number of runs
              </div>
              <div className="font-geist text-[18px] font-semibold leading-[28px] text-neutral-800 dark:text-neutral-200">
                {new Intl.NumberFormat().format(totalRuns)} runs
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
