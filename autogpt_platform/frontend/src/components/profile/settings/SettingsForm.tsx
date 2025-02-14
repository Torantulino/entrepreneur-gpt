"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { User } from "@supabase/supabase-js";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { updateSettings } from "@/app/profile/(user)/settings/actions";
import { toast } from "@/components/ui/use-toast";
import {
  NotificationPreference,
  NotificationPreferenceDTO,
} from "@/lib/autogpt-server-api";

const formSchema = z
  .object({
    email: z.string().email(),
    password: z
      .string()
      .optional()
      .refine((val) => {
        // If password is provided, it must be at least 8 characters
        if (val) return val.length >= 8;
        return true;
      }, "String must contain at least 8 character(s)"),
    confirmPassword: z.string().optional(),
    notifyOnAgentRun: z.boolean(),
    notifyOnZeroBalance: z.boolean(),
    notifyOnLowBalance: z.boolean(),
    notifyOnBlockExecutionFailed: z.boolean(),
    notifyOnContinuousAgentError: z.boolean(),
    notifyOnDailySummary: z.boolean(),
    notifyOnWeeklySummary: z.boolean(),
    notifyOnMonthlySummary: z.boolean(),
  })
  .refine(
    (data) => {
      if (data.password || data.confirmPassword) {
        return data.password === data.confirmPassword;
      }
      return true;
    },
    {
      message: "Passwords do not match",
      path: ["confirmPassword"],
    },
  );

interface SettingsFormProps {
  user: User;
  preferences: NotificationPreferenceDTO;
}

export default function SettingsForm({ user, preferences }: SettingsFormProps) {
  const defaultValues = {
    email: user.email || "",
    password: "",
    confirmPassword: "",
    notifyOnAgentRun: preferences.preferences.AGENT_RUN,
    notifyOnZeroBalance: preferences.preferences.ZERO_BALANCE,
    notifyOnLowBalance: preferences.preferences.LOW_BALANCE,
    notifyOnBlockExecutionFailed:
      preferences.preferences.BLOCK_EXECUTION_FAILED,
    notifyOnContinuousAgentError:
      preferences.preferences.CONTINUOUS_AGENT_ERROR,
    notifyOnDailySummary: preferences.preferences.DAILY_SUMMARY,
    notifyOnWeeklySummary: preferences.preferences.WEEKLY_SUMMARY,
    notifyOnMonthlySummary: preferences.preferences.MONTHLY_SUMMARY,
  };

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues,
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      const formData = new FormData();

      Object.entries(values).forEach(([key, value]) => {
        if (key !== "confirmPassword") {
          formData.append(key, value.toString());
        }
      });

      await updateSettings(formData);

      toast({
        title: "Successfully updated settings",
      });
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Something went wrong",
        variant: "destructive",
      });
      throw error;
    }
  }

  function onCancel() {
    form.reset(defaultValues);
  }
  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="flex flex-col gap-8"
      >
        {/* Account Settings Section */}
        <div className="flex flex-col gap-4">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input {...field} type="email" />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>New Password</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    type="password"
                    placeholder="************"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="confirmPassword"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Confirm New Password</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    type="password"
                    placeholder="************"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <Separator />

        {/* Notifications Section */}
        <div className="flex flex-col gap-6">
          <h3 className="text-lg font-medium">Notifications</h3>

          {/* Agent Notifications */}
          <div className="flex flex-col gap-4">
            <h4 className="text-sm font-medium text-muted-foreground">
              Agent Notifications
            </h4>
            <FormField
              control={form.control}
              name="notifyOnAgentRun"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">
                      Agent Run Notifications
                    </FormLabel>
                    <FormDescription>
                      Receive notifications when an agent starts or completes a
                      run
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="notifyOnBlockExecutionFailed"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">
                      Block Execution Failures
                    </FormLabel>
                    <FormDescription>
                      Get notified when a block execution fails during agent
                      runs
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="notifyOnContinuousAgentError"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">
                      Continuous Agent Errors
                    </FormLabel>
                    <FormDescription>
                      Receive alerts when an agent encounters repeated errors
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />
          </div>

          {/* Balance Notifications */}
          <div className="flex flex-col gap-4">
            <h4 className="text-sm font-medium text-muted-foreground">
              Balance Notifications
            </h4>
            <FormField
              control={form.control}
              name="notifyOnZeroBalance"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">
                      Zero Balance Alert
                    </FormLabel>
                    <FormDescription>
                      Get notified when your account balance reaches zero
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="notifyOnLowBalance"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">
                      Low Balance Warning
                    </FormLabel>
                    <FormDescription>
                      Receive warnings when your balance is running low
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />
          </div>

          {/* Summary Reports */}
          <div className="flex flex-col gap-4">
            <h4 className="text-sm font-medium text-muted-foreground">
              Summary Reports
            </h4>
            <FormField
              control={form.control}
              name="notifyOnDailySummary"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Daily Summary</FormLabel>
                    <FormDescription>
                      Receive a daily summary of your account activity
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="notifyOnWeeklySummary"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Weekly Summary</FormLabel>
                    <FormDescription>
                      Get a weekly overview of your account performance
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="notifyOnMonthlySummary"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Monthly Summary</FormLabel>
                    <FormDescription>
                      Receive a comprehensive monthly report of your account
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />
          </div>
        </div>

        {/* Form Actions */}
        <div className="flex justify-end gap-4">
          <Button
            variant="outline"
            type="button"
            onClick={onCancel}
            disabled={form.formState.isSubmitting}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={form.formState.isSubmitting || !form.formState.isDirty}
          >
            {form.formState.isSubmitting ? "Saving..." : "Save changes"}
          </Button>
        </div>
      </form>
    </Form>
  );
}
