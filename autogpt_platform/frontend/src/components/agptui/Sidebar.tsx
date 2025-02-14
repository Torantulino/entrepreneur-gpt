import * as React from "react";
import Link from "next/link";
import { Button } from "./Button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { KeyIcon, Menu } from "lucide-react";
import {
  IconDashboardLayout,
  IconIntegrations,
  IconProfile,
  IconSliders,
  IconCoin,
} from "../ui/icons";

interface SidebarLinkGroup {
  links: {
    text: string;
    href: string;
  }[];
}

interface SidebarProps {
  linkGroups: SidebarLinkGroup[];
}

export const Sidebar: React.FC<SidebarProps> = ({ linkGroups }) => {
  const stripeAvailable = Boolean(
    process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY,
  );

  return (
    <>
      <Sheet>
        <SheetTrigger asChild>
          <Button
            aria-label="Open sidebar menu"
            className="fixed left-4 top-4 z-50 flex h-14 w-14 items-center justify-center rounded-lg border border-neutral-500 bg-neutral-200 hover:bg-gray-200/50 dark:border-neutral-700 dark:bg-neutral-800 dark:hover:bg-gray-700/50 md:block lg:hidden"
          >
            <Menu className="h-8 w-8 stroke-black dark:stroke-white" />
            <span className="sr-only">Open sidebar menu</span>
          </Button>
        </SheetTrigger>
        <SheetContent
          side="left"
          className="z-50 w-[280px] border-none p-0 dark:bg-neutral-900 sm:w-[280px]"
        >
          <div className="h-full w-full rounded-2xl bg-zinc-200 dark:bg-zinc-800">
            <div className="inline-flex h-[264px] flex-col items-start justify-start gap-6 p-3">
              <Link
                href="/profile/dashboard"
                className="inline-flex w-full items-center gap-2.5 rounded-xl px-3 py-3 text-neutral-800 hover:bg-neutral-800 hover:text-white dark:text-neutral-200 dark:hover:bg-neutral-700 dark:hover:text-white"
              >
                <IconDashboardLayout className="h-6 w-6" />
                <div className="p-ui-medium text-base font-medium leading-normal">
                  Creator dashboard
                </div>
              </Link>
              {stripeAvailable && (
                <Link
                  href="/profile/credits"
                  className="inline-flex w-full items-center gap-2.5 rounded-xl px-3 py-3 text-neutral-800 hover:bg-neutral-800 hover:text-white dark:text-neutral-200 dark:hover:bg-neutral-700 dark:hover:text-white"
                >
                  <IconCoin className="h-6 w-6" />
                  <div className="p-ui-medium text-base font-medium leading-normal">
                    Billing
                  </div>
                </Link>
              )}
              <Link
                href="/profile/integrations"
                className="inline-flex w-full items-center gap-2.5 rounded-xl px-3 py-3 text-neutral-800 hover:bg-neutral-800 hover:text-white dark:text-neutral-200 dark:hover:bg-neutral-700 dark:hover:text-white"
              >
                <IconIntegrations className="h-6 w-6" />
                <div className="p-ui-medium text-base font-medium leading-normal">
                  Integrations
                </div>
              </Link>
              <Link
                href="/profile/api_keys"
                className="inline-flex w-full items-center gap-2.5 rounded-xl px-3 py-3 text-neutral-800 hover:bg-neutral-800 hover:text-white dark:text-neutral-200 dark:hover:bg-neutral-700 dark:hover:text-white"
              >
                <KeyIcon className="h-6 w-6" />
                <div className="p-ui-medium text-base font-medium leading-normal">
                  API Keys
                </div>
              </Link>
              <Link
                href="/profile"
                className="inline-flex w-full items-center gap-2.5 rounded-xl px-3 py-3 text-neutral-800 hover:bg-neutral-800 hover:text-white dark:text-neutral-200 dark:hover:bg-neutral-700 dark:hover:text-white"
              >
                <IconProfile className="h-6 w-6" />
                <div className="p-ui-medium text-base font-medium leading-normal">
                  Profile
                </div>
              </Link>
              <Link
                href="/profile/settings"
                className="inline-flex w-full items-center gap-2.5 rounded-xl px-3 py-3 text-neutral-800 hover:bg-neutral-800 hover:text-white dark:text-neutral-200 dark:hover:bg-neutral-700 dark:hover:text-white"
              >
                <IconSliders className="h-6 w-6" />
                <div className="p-ui-medium text-base font-medium leading-normal">
                  Settings
                </div>
              </Link>
            </div>
          </div>
        </SheetContent>
      </Sheet>

      <div className="relative hidden h-[912px] w-[234px] border-none lg:block">
        <div className="h-full w-full rounded-2xl bg-zinc-200 dark:bg-zinc-800">
          <div className="inline-flex h-[264px] flex-col items-start justify-start gap-6 p-3">
            <Link
              href="/profile/dashboard"
              className="inline-flex w-full items-center gap-2.5 rounded-xl px-3 py-3 text-neutral-800 hover:bg-neutral-800 hover:text-white dark:text-neutral-200 dark:hover:bg-neutral-700 dark:hover:text-white"
            >
              <IconDashboardLayout className="h-6 w-6" />
              <div className="p-ui-medium text-base font-medium leading-normal">
                Agent dashboard
              </div>
            </Link>
            {stripeAvailable && (
              <Link
                href="/profile/credits"
                className="inline-flex w-full items-center gap-2.5 rounded-xl px-3 py-3 text-neutral-800 hover:bg-neutral-800 hover:text-white dark:text-neutral-200 dark:hover:bg-neutral-700 dark:hover:text-white"
              >
                <IconCoin className="h-6 w-6" />
                <div className="p-ui-medium text-base font-medium leading-normal">
                  Billing
                </div>
              </Link>
            )}
            <Link
              href="/profile/integrations"
              className="inline-flex w-full items-center gap-2.5 rounded-xl px-3 py-3 text-neutral-800 hover:bg-neutral-800 hover:text-white dark:text-neutral-200 dark:hover:bg-neutral-700 dark:hover:text-white"
            >
              <IconIntegrations className="h-6 w-6" />
              <div className="p-ui-medium text-base font-medium leading-normal">
                Integrations
              </div>
            </Link>
            <Link
              href="/profile/api_keys"
              className="inline-flex w-full items-center gap-2.5 rounded-xl px-3 py-3 text-neutral-800 hover:bg-neutral-800 hover:text-white dark:text-neutral-200 dark:hover:bg-neutral-700 dark:hover:text-white"
            >
              <KeyIcon className="h-6 w-6" strokeWidth={1} />
              <div className="p-ui-medium text-base font-medium leading-normal">
                API Keys
              </div>
            </Link>
            <Link
              href="/profile"
              className="inline-flex w-full items-center gap-2.5 rounded-xl px-3 py-3 text-neutral-800 hover:bg-neutral-800 hover:text-white dark:text-neutral-200 dark:hover:bg-neutral-700 dark:hover:text-white"
            >
              <IconProfile className="h-6 w-6" />
              <div className="p-ui-medium text-base font-medium leading-normal">
                Profile
              </div>
            </Link>
            <Link
              href="/profile/settings"
              className="inline-flex w-full items-center gap-2.5 rounded-xl px-3 py-3 text-neutral-800 hover:bg-neutral-800 hover:text-white dark:text-neutral-200 dark:hover:bg-neutral-700 dark:hover:text-white"
            >
              <IconSliders className="h-6 w-6" />
              <div className="p-ui-medium text-base font-medium leading-normal">
                Settings
              </div>
            </Link>
          </div>
        </div>
      </div>
    </>
  );
};
