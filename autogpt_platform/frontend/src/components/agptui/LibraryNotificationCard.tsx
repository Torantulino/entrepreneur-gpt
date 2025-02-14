import { Button } from "../ui/button";
import Image from "next/image";
import { Separator } from "../ui/separator";
import {
  CirclePlayIcon,
  ClipboardCopy,
  ImageIcon,
  Play,
  PlayCircle,
  Share2,
  X,
} from "lucide-react";
import { Dispatch, SetStateAction } from "react";

export interface NotificationCardData {
  type: "text" | "image" | "video" | "audio";
  title: string;
  id: string;
  content?: string;
  mediaUrl?: string;
}

interface NotificationCardProps extends NotificationCardData {
  setNotifications: Dispatch<SetStateAction<NotificationCardData[] | null>>;
}

const NotificationCard = ({
  type,
  title,
  id,
  content,
  mediaUrl,
  setNotifications,
}: NotificationCardProps) => {
  const barHeights = Array.from({ length: 60 }, () =>
    Math.floor(Math.random() * (34 - 20 + 1) + 20),
  );

  const handleClose = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    setNotifications((prev) => {
      if (!prev) return null;
      return prev.filter((notification) => notification.id !== id);
    });
  };

  return (
    <div className="w-[430px] space-y-[22px] rounded-[14px] border border-neutral-100 bg-neutral-50 p-[16px] pt-[12px]">
      <div className="flex items-center justify-between">
        {/* count */}
        <div className="flex items-center gap-[10px]">
          <p className="font-sans text-[12px] font-medium text-neutral-500">
            1/4
          </p>
          <p className="h-[26px] rounded-[45px] bg-green-100 px-[9px] py-[3px] font-sans text-[12px] font-medium text-green-800">
            Success
          </p>
        </div>

        {/* cross icon */}
        <Button
          variant="ghost"
          className="p-0 hover:bg-transparent"
          onClick={handleClose}
        >
          <X
            className="h-6 w-6 text-[#020617] hover:scale-105"
            strokeWidth={1.25}
          />
        </Button>
      </div>

      <div className="space-y-[6px] p-0">
        <p className="font-sans text-[14px] font-medium leading-[20px] text-neutral-500">
          New Output Ready!
        </p>
        <h2 className="font-poppin text-[20px] font-medium leading-7 text-neutral-800">
          {title}
        </h2>
        {type === "text" && <Separator />}
      </div>

      <div className="p-0">
        {type === "text" && (
          // Maybe in future we give markdown support
          <div className="mt-[-8px] line-clamp-6 font-sans text-sm font-[400px] text-neutral-600">
            {content}
          </div>
        )}

        {type === "image" &&
          (mediaUrl ? (
            <div className="relative h-[200px] w-full">
              <Image
                src={mediaUrl}
                alt={title}
                fill
                className="rounded-lg object-cover"
              />
            </div>
          ) : (
            <div className="flex h-[244px] w-full items-center justify-center rounded-lg bg-[#D9D9D9]">
              <ImageIcon
                className="h-[138px] w-[138px] text-neutral-400"
                strokeWidth={1}
              />
            </div>
          ))}

        {type === "video" && (
          <div className="space-y-4">
            {mediaUrl ? (
              <video src={mediaUrl} controls className="w-full rounded-lg" />
            ) : (
              <div className="flex h-[219px] w-[398px] items-center justify-center rounded-lg bg-[#D9D9D9]">
                <PlayCircle
                  className="h-16 w-16 text-neutral-500"
                  strokeWidth={1}
                />
              </div>
            )}
          </div>
        )}

        {type === "audio" && (
          <div className="flex gap-2">
            <CirclePlayIcon
              className="h-10 w-10 rounded-full bg-neutral-800 text-white"
              strokeWidth={1}
            />
            <div className="flex flex-1 items-center justify-between">
              {/* <audio src={mediaUrl} controls className="w-full" /> */}
              {barHeights.map((h, i) => {
                return (
                  <div
                    key={i}
                    className={`rounded-[8px] bg-neutral-500`}
                    style={{
                      height: `${h}px`,
                      width: "3px",
                    }}
                  />
                );
              })}
            </div>
          </div>
        )}
      </div>

      <div className="flex justify-between gap-2 p-0">
        <div className="space-x-3">
          <Button
            variant="outline"
            onClick={() => {
              navigator.share({
                title,
                text: content,
                url: mediaUrl,
              });
            }}
            className="h-10 w-10 rounded-full border-neutral-800 p-0"
          >
            <Share2 className="h-5 w-5" strokeWidth={1} />
          </Button>
          <Button
            variant="outline"
            onClick={() =>
              navigator.clipboard.writeText(content || mediaUrl || "")
            }
            className="h-10 w-10 rounded-full border-neutral-800 p-0"
          >
            <ClipboardCopy className="h-5 w-5" strokeWidth={1} />
          </Button>
        </div>
        <Button className="h-[40px] rounded-[52px] bg-neutral-800 px-4 py-2">
          See run
        </Button>
      </div>
    </div>
  );
};

export default NotificationCard;
