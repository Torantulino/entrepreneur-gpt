import * as React from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@/components/ui/popover";
import {
  IconType,
  IconEdit,
  IconLayoutDashboard,
  IconUploadCloud,
  IconSettings,
  IconLogOut,
  IconRefresh,
  IconMarketplace,
  IconLibrary,
  IconBuilder,
} from "../ui/icons";
import Link from "next/link";
import { ProfilePopoutMenuLogoutButton } from "./ProfilePopoutMenuLogoutButton";
import { PublishAgentPopout } from "./composite/PublishAgentPopout";

interface ProfilePopoutMenuProps {
  userName?: string;
  userEmail?: string;
  avatarSrc?: string;
  hideNavBarUsername?: boolean;
  menuItemGroups: {
    groupName?: string;
    items: {
      icon: IconType;
      text: string;
      href?: string;
      onClick?: () => void;
    }[];
  }[];
}

export const ProfilePopoutMenu: React.FC<ProfilePopoutMenuProps> = ({
  userName,
  userEmail,
  avatarSrc,
  menuItemGroups,
}) => {
  const popupId = React.useId();

  const getIcon = (icon: IconType) => {
    const iconClass = "w-6 h-6";
    switch (icon) {
      case IconType.LayoutDashboard:
        return <IconLayoutDashboard className={iconClass} />;
      case IconType.UploadCloud:
        return <IconUploadCloud className={iconClass} />;
      case IconType.Edit:
        return <IconEdit className={iconClass} />;
      case IconType.Settings:
        return <IconSettings className={iconClass} />;
      case IconType.LogOut:
        return <IconLogOut className={iconClass} />;
      case IconType.Marketplace:
        return <IconMarketplace className={iconClass} />;
      case IconType.Library:
        return <IconLibrary className={iconClass} />;
      case IconType.Builder:
        return <IconBuilder className={iconClass} />;
      default:
        return <IconRefresh className={iconClass} />;
    }
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <button
          type="button"
          className="flex cursor-pointer items-center space-x-3"
          aria-label="Open profile menu"
          aria-controls={popupId}
          aria-haspopup="true"
          data-testid="profile-popout-menu-trigger"
        >
          <Avatar className="h-10 w-10">
            <AvatarImage src={avatarSrc} alt="" aria-hidden="true" />
            <AvatarFallback aria-hidden="true">
              {userName?.charAt(0) || "U"}
            </AvatarFallback>
          </Avatar>
        </button>
      </PopoverTrigger>

      <PopoverContent
        id={popupId}
        className="flex h-[380px] w-[300px] flex-col items-start justify-start gap-4 rounded-[26px] bg-zinc-400/70 p-6 shadow-sm backdrop-blur-2xl dark:bg-zinc-800/70"
      >
        {/* Header with avatar and user info */}
        <div className="inline-flex items-center justify-start gap-4 self-stretch">
          <Avatar className="h-[60px] w-[60px]">
            <AvatarImage src={avatarSrc} alt="" aria-hidden="true" />
            <AvatarFallback aria-hidden="true">
              {userName?.charAt(0) || "U"}
            </AvatarFallback>
          </Avatar>
          <div className="relative h-[47px] w-[173px]">
            <div className="absolute left-0 top-0 font-['Geist'] text-base font-semibold leading-7 text-white dark:text-neutral-200">
              {userName}
            </div>
            <div className="absolute left-0 top-[23px] font-['Geist'] text-base font-normal leading-normal text-white dark:text-neutral-400">
              {userEmail}
            </div>
          </div>
        </div>

        {/* Menu items */}
        <div className="flex w-full flex-col items-start justify-start gap-1.5 rounded-[23px]">
          {menuItemGroups.map((group, groupIndex) => (
            <div
              key={groupIndex}
              className="flex w-full flex-col items-start justify-start gap-5 rounded-[18px] bg-white p-3.5 dark:bg-neutral-900"
            >
              {group.items.map((item, itemIndex) => {
                if (item.href) {
                  return (
                    <Link
                      key={itemIndex}
                      href={item.href}
                      className="inline-flex w-full items-center justify-start gap-2.5"
                    >
                      <div className="relative h-6 w-6">
                        {getIcon(item.icon)}
                      </div>
                      <div className="font-['Geist'] text-base font-medium leading-normal text-neutral-800 dark:text-neutral-200">
                        {item.text}
                      </div>
                    </Link>
                  );
                } else if (item.text === "Log out") {
                  return <ProfilePopoutMenuLogoutButton key={itemIndex} />;
                } else if (item.text === "Publish an agent") {
                  return (
                    <PublishAgentPopout
                      key={itemIndex}
                      trigger={
                        <div className="inline-flex w-full items-center justify-start gap-2.5">
                          <div className="relative h-6 w-6">
                            {getIcon(item.icon)}
                          </div>
                          <div className="font-['Geist'] text-base font-medium leading-normal text-neutral-800 dark:text-neutral-200">
                            {item.text}
                          </div>
                        </div>
                      }
                      inputStep="select"
                      submissionData={undefined}
                      openPopout={false}
                    />
                  );
                } else {
                  return (
                    <div
                      key={itemIndex}
                      className="inline-flex w-full items-center justify-start gap-2.5"
                      onClick={item.onClick}
                      role="button"
                      tabIndex={0}
                    >
                      <div className="relative h-6 w-6">
                        {getIcon(item.icon)}
                      </div>
                      <div className="font-['Geist'] text-base font-medium leading-normal text-neutral-800 dark:text-neutral-200">
                        {item.text}
                      </div>
                    </div>
                  );
                }
              })}
            </div>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
};
