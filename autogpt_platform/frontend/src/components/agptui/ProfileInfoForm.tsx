"use client";

import * as React from "react";
import { useState } from "react";

import Image from "next/image";

import { Button } from "./Button";
import { IconPersonFill } from "@/components/ui/icons";
import { CreatorDetails, ProfileDetails } from "@/lib/autogpt-server-api/types";
import { Separator } from "@/components/ui/separator";
import useSupabase from "@/hooks/useSupabase";
import { useBackendAPI } from "@/lib/autogpt-server-api/context";

export const ProfileInfoForm = ({ profile }: { profile: CreatorDetails }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [profileData, setProfileData] = useState(profile);
  const { supabase } = useSupabase();
  const api = useBackendAPI();

  const submitForm = async () => {
    try {
      setIsSubmitting(true);

      const updatedProfile = {
        name: profileData.name,
        username: profileData.username,
        description: profileData.description,
        links: profileData.links.filter((link) => link), // Filter out empty links
        avatar_url: profileData.avatar_url,
      };

      if (!isSubmitting) {
        const returnedProfile = await api.updateStoreProfile(
          updatedProfile as ProfileDetails,
        );
        setProfileData(returnedProfile as CreatorDetails);
      }
    } catch (error) {
      console.error("Error updating profile:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleImageUpload = async (file: File) => {
    try {
      // Create FormData and append file
      const formData = new FormData();
      formData.append("file", file);

      console.log(formData);

      // Get auth token
      if (!supabase) {
        throw new Error("Supabase client not initialized");
      }

      const {
        data: { session },
      } = await supabase.auth.getSession();
      const token = session?.access_token;

      if (!token) {
        throw new Error("No authentication token found");
      }

      // Make upload request
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_AGPT_SERVER_URL}/store/submissions/media`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        },
      );

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      // Get media URL from response
      const mediaUrl = await response.json();

      // Update profile with new avatar URL
      const updatedProfile = {
        ...profileData,
        avatar_url: mediaUrl,
      };

      const returnedProfile = await api.updateStoreProfile(
        updatedProfile as ProfileDetails,
      );
      setProfileData(returnedProfile as CreatorDetails);
    } catch (error) {
      console.error("Error uploading image:", error);
    }
  };

  return (
    <div className="w-full min-w-[800px] px-4 sm:px-8">
      <h1 className="font-circular mb-6 text-[28px] font-normal text-neutral-900 dark:text-neutral-100 sm:mb-8 sm:text-[35px]">
        Profile
      </h1>

      <div className="mb-8 sm:mb-12">
        <div className="mb-8 flex flex-col items-center gap-4 sm:flex-row sm:items-start">
          <div className="relative h-[130px] w-[130px] rounded-full bg-[#d9d9d9] dark:bg-[#333333]">
            {profileData.avatar_url ? (
              <Image
                src={profileData.avatar_url}
                alt="Profile"
                fill
                className="rounded-full"
              />
            ) : (
              <IconPersonFill className="absolute left-[30px] top-[24px] h-[77.80px] w-[70.63px] text-[#7e7e7e] dark:text-[#999999]" />
            )}
          </div>
          <label className="font-circular mt-11 inline-flex h-[43px] items-center justify-center rounded-[22px] bg-[#15171A] px-6 py-2 text-sm font-normal text-white transition-colors hover:bg-[#2D2F34] dark:bg-white dark:text-[#15171A] dark:hover:bg-[#E5E5E5]">
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={async (e) => {
                const file = e.target.files?.[0];
                if (file) {
                  await handleImageUpload(file);
                }
              }}
            />
            Edit photo
          </label>
        </div>

        <form className="space-y-4 sm:space-y-6" onSubmit={submitForm}>
          <div className="w-full">
            <label className="font-circular mb-1.5 block text-base font-normal leading-tight text-neutral-700 dark:text-neutral-300">
              Display name
            </label>
            <div className="rounded-[55px] border border-slate-200 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800">
              <input
                type="text"
                name="displayName"
                defaultValue={profileData.name}
                placeholder="Enter your display name"
                className="font-circular w-full border-none bg-transparent text-base font-normal text-neutral-900 placeholder:text-neutral-400 focus:outline-none dark:text-white dark:placeholder:text-neutral-500"
                onChange={(e) => {
                  const newProfileData = {
                    ...profileData,
                    name: e.target.value,
                  };
                  setProfileData(newProfileData);
                }}
              />
            </div>
          </div>

          <div className="w-full">
            <label className="font-circular mb-1.5 block text-base font-normal leading-tight text-neutral-700 dark:text-neutral-300">
              Handle
            </label>
            <div className="rounded-[55px] border border-slate-200 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800">
              <input
                type="text"
                name="handle"
                defaultValue={profileData.username}
                placeholder="@username"
                className="font-circular w-full border-none bg-transparent text-base font-normal text-neutral-900 placeholder:text-neutral-400 focus:outline-none dark:text-white dark:placeholder:text-neutral-500"
                onChange={(e) => {
                  const newProfileData = {
                    ...profileData,
                    username: e.target.value,
                  };
                  setProfileData(newProfileData);
                }}
              />
            </div>
          </div>

          <div className="w-full">
            <label className="font-circular mb-1.5 block text-base font-normal leading-tight text-neutral-700 dark:text-neutral-300">
              Bio
            </label>
            <div className="h-[220px] rounded-2xl border border-slate-200 py-2.5 pl-4 pr-4 dark:border-slate-700 dark:bg-slate-800">
              <textarea
                name="bio"
                defaultValue={profileData.description}
                placeholder="Tell us about yourself..."
                className="font-circular h-full w-full resize-none border-none bg-transparent text-base font-normal text-neutral-900 placeholder:text-neutral-400 focus:outline-none dark:text-white dark:placeholder:text-neutral-500"
                onChange={(e) => {
                  const newProfileData = {
                    ...profileData,
                    description: e.target.value,
                  };
                  setProfileData(newProfileData);
                }}
              />
            </div>
          </div>

          <section className="mb-8">
            <h2 className="font-circular mb-4 text-lg font-normal leading-7 text-neutral-700 dark:text-neutral-300">
              Your links
            </h2>
            <p className="font-circular mb-6 text-base font-normal leading-tight text-neutral-600 dark:text-neutral-400">
              You can display up to 5 links on your profile
            </p>

            <div className="space-y-4 sm:space-y-6">
              {[1, 2, 3, 4, 5].map((linkNum) => {
                const link = profileData.links[linkNum - 1];
                return (
                  <div key={linkNum} className="w-full">
                    <label className="font-circular mb-1.5 block text-base font-normal leading-tight text-neutral-700 dark:text-neutral-300">
                      Link {linkNum}
                    </label>
                    <div className="rounded-[55px] border border-slate-200 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800">
                      <input
                        type="text"
                        name={`link${linkNum}`}
                        placeholder="https://"
                        defaultValue={link || ""}
                        className="font-circular w-full border-none bg-transparent text-base font-normal text-neutral-900 placeholder:text-neutral-400 focus:outline-none dark:text-white dark:placeholder:text-neutral-500"
                        onChange={(e) => {
                          const newLinks = [...profileData.links];
                          newLinks[linkNum - 1] = e.target.value;
                          const newProfileData = {
                            ...profileData,
                            links: newLinks,
                          };
                          setProfileData(newProfileData);
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          <Separator />

          <div className="flex h-[50px] items-center justify-end gap-3 py-8">
            <Button
              type="button"
              variant="secondary"
              className="font-circular h-[50px] rounded-[35px] bg-neutral-200 px-6 py-3 text-base font-medium text-neutral-800 transition-colors hover:bg-neutral-300 dark:border-neutral-700 dark:bg-neutral-700 dark:text-neutral-200 dark:hover:border-neutral-600 dark:hover:bg-neutral-600"
              onClick={() => {
                setProfileData(profile);
              }}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="font-circular h-[50px] rounded-[35px] bg-neutral-800 px-6 py-3 text-base font-medium text-white transition-colors hover:bg-neutral-900 dark:bg-neutral-200 dark:text-neutral-900 dark:hover:bg-neutral-100"
              onClick={submitForm}
            >
              {isSubmitting ? "Saving..." : "Save changes"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
