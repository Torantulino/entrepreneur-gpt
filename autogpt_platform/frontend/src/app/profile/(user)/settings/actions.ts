"use server";

import { revalidatePath } from "next/cache";
import getServerSupabase from "@/lib/supabase/getServerSupabase";
import BackendApi from "@/lib/autogpt-server-api";
import { NotificationPreferenceDTO } from "@/lib/autogpt-server-api/types";

export async function updateSettings(formData: FormData) {
  const supabase = getServerSupabase();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  // Handle auth-related updates
  const password = formData.get("password") as string;
  const email = formData.get("email") as string;

  if (password) {
    const { error: passwordError } = await supabase.auth.updateUser({
      password,
    });

    if (passwordError) {
      throw new Error(`${passwordError.message}`);
    }
  }

  if (email !== user?.email) {
    const { error: emailError } = await supabase.auth.updateUser({
      email,
    });
    const api = new BackendApi();
    await api.updateUserEmail(email);

    if (emailError) {
      throw new Error(`${emailError.message}`);
    }
  }

  try {
    const api = new BackendApi();
    const preferences: NotificationPreferenceDTO = {
      email: user?.email || "",
      preferences: {
        AGENT_RUN: formData.get("notifyOnAgentRun") === "true",
        ZERO_BALANCE: formData.get("notifyOnZeroBalance") === "true",
        LOW_BALANCE: formData.get("notifyOnLowBalance") === "true",
        BLOCK_EXECUTION_FAILED:
          formData.get("notifyOnBlockExecutionFailed") === "true",
        CONTINUOUS_AGENT_ERROR:
          formData.get("notifyOnContinuousAgentError") === "true",
        DAILY_SUMMARY: formData.get("notifyOnDailySummary") === "true",
        WEEKLY_SUMMARY: formData.get("notifyOnWeeklySummary") === "true",
        MONTHLY_SUMMARY: formData.get("notifyOnMonthlySummary") === "true",
      },
      daily_limit: 0,
    };
    await api.updateUserPreferences(preferences);
  } catch (error) {
    console.error(error);
    throw new Error(`Failed to update preferences: ${error}`);
  }

  revalidatePath("/profile/settings");
  return { success: true };
}

export async function getUserPreferences(): Promise<NotificationPreferenceDTO> {
  const api = new BackendApi();
  const preferences = await api.getUserPreferences();
  return preferences;
}
