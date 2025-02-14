import * as React from "react";
import { Sidebar } from "@/components/agptui/Sidebar";

export default function Layout({ children }: { children: React.ReactNode }) {
  const sidebarLinkGroups = [
    {
      links: [
        { text: "Creator Dashboard", href: "/profile/dashboard" },
        { text: "Agent dashboard", href: "/profile/agent-dashboard" },
        { text: "Billing", href: "/profile/credits" },
        { text: "Integrations", href: "/profile/integrations" },
        { text: "API Keys", href: "/profile/api_keys" },
        { text: "Profile", href: "/profile" },
        { text: "Settings", href: "/profile/settings" },
      ],
    },
  ];

  return (
    <div className="flex min-h-screen w-screen max-w-[1360px] flex-col lg:flex-row">
      <Sidebar linkGroups={sidebarLinkGroups} />
      <div className="flex-1 pl-4">{children}</div>
    </div>
  );
}
