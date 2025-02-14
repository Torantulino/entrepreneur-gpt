import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";

export default function SettingsLoading() {
  return (
    <div className="container max-w-2xl py-10">
      <div className="space-y-6">
        <div>
          <Skeleton className="h-6 w-32" />
          <Skeleton className="mt-2 h-4 w-96" />
        </div>

        <div className="space-y-8">
          <div className="space-y-4">
            {/* Email and Password fields */}
            {[1, 2].map((i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-16" />
                <Skeleton className="h-10 w-full" />
              </div>
            ))}
          </div>

          <Separator />

          <div className="space-y-4">
            <Skeleton className="h-6 w-28" />

            {/* Agent Notifications */}
            <div className="space-y-4">
              <Skeleton className="h-4 w-36" />
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="flex flex-row items-center justify-between rounded-lg p-4"
                >
                  <div className="space-y-0.5">
                    <Skeleton className="h-5 w-48" />
                    <Skeleton className="h-4 w-72" />
                  </div>
                  <Skeleton className="h-6 w-11" />
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-end space-x-4">
            <Skeleton className="h-10 w-24" />
            <Skeleton className="h-10 w-32" />
          </div>
        </div>
      </div>
    </div>
  );
}
