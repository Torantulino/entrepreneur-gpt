"use client";

import { LibraryPageProvider } from "@/components/agptui/providers/LibraryAgentProvider";
import React from "react";

export default function Layout({ children }: { children: React.ReactNode }) {
  return <LibraryPageProvider>{children}</LibraryPageProvider>;
}
