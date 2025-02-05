export default function AgentsFlowListSkeleton() {
  return (
    <div className="mx-auto max-w-4xl p-4">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Agents</h1>
        <div className="h-10 w-24 animate-pulse rounded bg-gray-200"></div>
      </div>
      <div className="rounded-lg bg-white p-4 shadow-sm">
        <div className="mb-4 grid grid-cols-3 gap-4 font-medium text-gray-500">
          <div>Name</div>
          <div># of runs</div>
          <div>Last run</div>
        </div>
        {[...Array(3)].map((_, index) => (
          <div key={index} className="mb-4 grid grid-cols-3 gap-4">
            <div className="h-6 animate-pulse rounded bg-gray-200"></div>
            <div className="h-6 animate-pulse rounded bg-gray-200"></div>
            <div className="h-6 animate-pulse rounded bg-gray-200"></div>
          </div>
        ))}
      </div>
    </div>
  );
}
