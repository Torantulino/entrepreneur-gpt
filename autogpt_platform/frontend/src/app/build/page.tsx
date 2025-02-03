"use client";

import { useSearchParams } from "next/navigation";
import FlowEditor from "@/components/Flow";

export default function Home() {
  const query = useSearchParams();

  return (
    <FlowEditor
      className="flow-container"
      flowID={query.get("flowID") ?? undefined}
      flowVersion={query.get("flowVersion") ?? undefined}
    />
  );
}
