import * as React from "react";
import { Metadata } from "next";
import SettingsForm from "@/components/profile/settings/SettingsForm";
import getServerUser from "@/lib/supabase/getServerUser";
import { redirect } from "next/navigation";
import { getUserPreferences } from "./actions";
export const metadata: Metadata = {
  title: "Settings",
  description: "Manage your account settings and preferences.",
};

export default async function SettingsPage() {
  const { user, error } = await getServerUser();

  if (error || !user) {
    redirect("/login");
  }

  const preferences = await getUserPreferences();

  return (
    <div className="container max-w-2xl space-y-6 py-10">
      <div>
        <h3 className="text-lg font-medium">My account</h3>
        <p className="text-sm text-muted-foreground">
          Manage your account settings and preferences.
        </p>
      </div>
      <SettingsForm user={user} preferences={preferences} />
    </div>
  );
}
