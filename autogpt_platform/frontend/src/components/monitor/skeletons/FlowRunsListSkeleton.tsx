export default function FlowRunsListSkeleton() {
  return (
    <div className="mx-auto max-w-4xl p-4">
      <div className="rounded-lg bg-white p-4 shadow-sm">
        <h2 className="mb-4 text-xl font-semibold">Runs</h2>
        <div className="mb-4 grid grid-cols-4 gap-4 text-sm font-medium text-gray-500">
          <div>Agent</div>
          <div>Started</div>
          <div>Status</div>
          <div>Duration</div>
        </div>
        {[...Array(4)].map((_, index) => (
          <div key={index} className="mb-4 grid grid-cols-4 gap-4">
            <div className="h-5 animate-pulse rounded bg-gray-200"></div>
            <div className="h-5 animate-pulse rounded bg-gray-200"></div>
            <div className="h-5 animate-pulse rounded bg-gray-200"></div>
            <div className="h-5 animate-pulse rounded bg-gray-200"></div>
          </div>
        ))}
      </div>
    </div>
  );
}
