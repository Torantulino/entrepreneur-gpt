import Link from "next/link";
import { Button } from "@/components/ui/button";
import React from "react";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import Image from "next/image";
import getServerUser from "@/lib/supabase/getServerUser";
import ProfileDropdown from "./ProfileDropdown";
import { IconCircleUser, IconMenu } from "@/components/ui/icons";
import CreditButton from "@/components/nav/CreditButton";
import { NavBarButtons } from "./nav/NavBarButtons";

export async function NavBar() {
  const isAvailable = Boolean(
    process.env.NEXT_PUBLIC_SUPABASE_URL &&
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  );
  const { user } = await getServerUser();

  return user ? (
    <header className="sticky top-0 z-50 mx-4 flex h-16 select-none items-center gap-4 border border-gray-300 bg-background p-3 md:rounded-b-2xl md:px-6 md:shadow-sm">
      <div className="flex flex-1 items-center gap-4">
        <Sheet>
          <SheetTrigger asChild>
            <Button
              variant="outline"
              size="icon"
              className="shrink-0 md:hidden"
            >
              <IconMenu />
              <span className="sr-only">Toggle navigation menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="left">
            <nav className="grid gap-6 text-lg font-medium">
              <NavBarButtons className="flex flex-row items-center gap-2" />
            </nav>
          </SheetContent>
        </Sheet>
        <nav className="hidden md:flex md:flex-row md:items-center md:gap-5 lg:gap-8">
          <div className="flex h-10 w-20 flex-1 flex-row items-center justify-center gap-2">
            <a href="https://agpt.co/">
              <Image
                src="/AUTOgpt_Logo_dark.png"
                alt="AutoGPT Logo"
                width={100}
                height={40}
                priority
              />
            </a>
          </div>
          <NavBarButtons className="flex flex-row items-center gap-1 border border-white font-semibold hover:border-gray-900" />
        </nav>
      </div>
      <div className="flex flex-1 items-center justify-end gap-4">
        {isAvailable && user && <CreditButton />}

        {isAvailable && !user && (
          <Link
            href="/login"
            className="flex flex-row items-center gap-2 text-muted-foreground hover:text-foreground"
          >
            Log In
            <IconCircleUser />
          </Link>
        )}
        {isAvailable && user && <ProfileDropdown />}
      </div>
    </header>
  ) : (
    <nav className="flex w-full items-center p-2 pt-8">
      <div className="flex h-10 w-20 flex-1 flex-row items-center justify-center gap-2">
        <a href="https://agpt.co/">
          <Image
            src="/AUTOgpt_Logo_dark.png"
            alt="AutoGPT Logo"
            width={100}
            height={40}
            priority
          />
        </a>
      </div>
    </nav>
  );
}
