import { cn } from "@/lib/utils";
import Link from "next/link";
import Image from "next/image";
import { LibraryAgent } from "@/lib/autogpt-server-api";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export const LibraryAgentCard = ({
  id,
  name,
  can_access_graph,
  description,
  creator_image_url,
  image_url,
}: LibraryAgent) => {
  return (
    <div className="inline-flex w-full max-w-[434px] cursor-pointer flex-col items-start justify-start gap-2.5 rounded-[26px] bg-white transition-all duration-300 hover:shadow-lg dark:bg-transparent dark:hover:shadow-gray-700">
      <div className="relative h-[200px] w-full overflow-hidden rounded-[20px]">
        {!image_url ? (
          <div
            className={`h-full w-full ${
              [
                "bg-gradient-to-r from-green-200 to-blue-200",
                "bg-gradient-to-r from-pink-200 to-purple-200",
                "bg-gradient-to-r from-yellow-200 to-orange-200",
                "bg-gradient-to-r from-blue-200 to-cyan-200",
                "bg-gradient-to-r from-indigo-200 to-purple-200",
              ][Math.floor(Math.random() * 5)]
            }`}
            style={{
              backgroundSize: "200% 200%",
              animation: "gradient 15s ease infinite",
            }}
          />
        ) : (
          <Image
            src={image_url}
            alt={`${name} preview image`}
            fill
            className="object-cover"
            priority
          />
        )}
        <div className="absolute bottom-4 left-4">
          <Avatar className="h-16 w-16 border-2 border-white dark:border-gray-800">
            <AvatarImage
              src={
                creator_image_url
                  ? creator_image_url
                  : "/avatar-placeholder.png"
              }
              alt={`${name} creator avatar`}
            />
            <AvatarFallback>{name.charAt(0)}</AvatarFallback>
          </Avatar>
        </div>
      </div>

      <div className="flex w-full flex-1 flex-col px-4 py-4">
        <h3 className="font-poppins mb-2 text-2xl font-semibold leading-tight text-[#272727] dark:text-neutral-100">
          {name}
        </h3>

        <p className="mb-4 flex-1 text-sm text-gray-600 dark:text-gray-400">
          {description}
        </p>

        <div className="items-between mt-4 flex w-full justify-between">
          <div className="flex gap-3">
            <Link
              href={`/agents/${id}`}
              className="font-geist text-lg font-semibold text-neutral-800 hover:underline dark:text-neutral-200"
            >
              See runs
            </Link>

            {!can_access_graph && (
              <Link
                href={`/build?flowID=${id}`}
                className="font-geist text-lg font-semibold text-neutral-800 hover:underline dark:text-neutral-200"
              >
                Open in builder
              </Link>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
