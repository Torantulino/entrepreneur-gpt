"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import { ThemeProviderProps } from "next-themes";
import { BackendAPIProvider } from "@/lib/autogpt-server-api/context";
import { TooltipProvider } from "@/components/ui/tooltip";
import CredentialsProvider from "@/components/integrations/credentials-provider";
import { LaunchDarklyProvider } from "@/components/feature-flag/feature-flag-provider";

export interface ProvidersProps extends ThemeProviderProps {
  children: React.ReactNode;
  useMockBackend?: boolean;
}

export function Providers({
  children,
  useMockBackend,
  ...props
}: ProvidersProps) {
  return (
    <NextThemesProvider {...props}>
      <BackendAPIProvider useMockBackend={useMockBackend}>
        <CredentialsProvider>
          <LaunchDarklyProvider>
            <TooltipProvider>{children}</TooltipProvider>
          </LaunchDarklyProvider>
        </CredentialsProvider>
      </BackendAPIProvider>
    </NextThemesProvider>
  );
}
