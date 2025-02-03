export default function FlowRunsStatusSkeleton() {
  return (
    <div className="mx-auto max-w-4xl p-4">
      <div className="rounded-lg bg-white p-4 shadow-sm">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-xl font-semibold">Stats</h2>
          <div className="flex space-x-2">
            {["2h", "8h", "24h", "7d", "Custom", "All"].map((btn) => (
              <div
                key={btn}
                className="h-8 w-16 animate-pulse rounded bg-gray-200"
              ></div>
            ))}
          </div>
        </div>

        {/* Placeholder for the line chart */}
        <div className="mb-6 h-64 w-full animate-pulse rounded bg-gray-200"></div>

        {/* Placeholders for total runs and total run time */}
        <div className="space-y-2">
          <div className="h-6 w-1/3 animate-pulse rounded bg-gray-200"></div>
          <div className="h-6 w-1/2 animate-pulse rounded bg-gray-200"></div>
        </div>
      </div>
    </div>
  );
}
