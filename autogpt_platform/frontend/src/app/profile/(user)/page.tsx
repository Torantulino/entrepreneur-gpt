import * as React from "react";
import { ProfileInfoForm } from "@/components/agptui/ProfileInfoForm";
import BackendAPI from "@/lib/autogpt-server-api";
import { CreatorDetails } from "@/lib/autogpt-server-api/types";

async function getProfileData(api: BackendAPI) {
  try {
    const profile = await api.getStoreProfile("profile");
    return {
      profile,
    };
  } catch (error) {
    console.error("Error fetching profile:", error);
    return {
      profile: null,
    };
  }
}

export default async function Page({}: {}) {
  const api = new BackendAPI();
  const { profile } = await getProfileData(api);

  if (!profile) {
    return (
      <div className="flex flex-col items-center justify-center p-4">
        <p>Please log in to view your profile</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center px-4">
      <ProfileInfoForm profile={profile as CreatorDetails} />
    </div>
  );
}
