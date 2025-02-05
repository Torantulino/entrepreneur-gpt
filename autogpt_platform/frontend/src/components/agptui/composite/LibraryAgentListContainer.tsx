"use client";
import { useEffect, useState, useCallback } from "react";
import { LibraryAgentCard } from "../LibraryAgentCard";
import { useBackendAPI } from "@/lib/autogpt-server-api/context";
import { GraphMeta } from "@/lib/autogpt-server-api";
import { useThreshold } from "@/hooks/useThreshold";
import { useLibraryPageContext } from "../providers/LibraryAgentProvider";

interface LibraryAgentListContainerProps {}

export type AgentStatus =
  | "healthy"
  | "something wrong"
  | "waiting for trigger"
  | "Nothing running";

/**
 * LibraryAgentListContainer is a React component that displays a grid of library agents with infinite scroll functionality.
 */

const LibraryAgentListContainer: React.FC<
  LibraryAgentListContainerProps
> = ({}) => {
  const [nextToken, setNextToken] = useState<string | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);

  const api = useBackendAPI();
  const { agents, setAgents, setAgentLoading, agentLoading } =
    useLibraryPageContext();

  const fetchAgents = useCallback(
    async (paginationToken?: string) => {
      try {
        const response = await api.listLibraryAgents(paginationToken);
        if (paginationToken) {
          setAgents((prevAgent) => [...prevAgent, ...response.agents]);
        } else {
          setAgents(response.agents);
        }
        setNextToken(response.next_token);
      } finally {
        setAgentLoading(false);
        setLoadingMore(false);
      }
    },
    [api, setAgents, setAgentLoading],
  );

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  const handleInfiniteScroll = useCallback(
    (scrollY: number) => {
      if (!nextToken || loadingMore) return;

      const { scrollHeight, clientHeight } = document.documentElement;
      const SCROLL_THRESHOLD = 20;
      const FETCH_DELAY = 1000;

      if (scrollY + clientHeight >= scrollHeight - SCROLL_THRESHOLD) {
        setLoadingMore(true);
        setTimeout(() => fetchAgents(nextToken), FETCH_DELAY);
      }
    },
    [nextToken, loadingMore, fetchAgents],
  );

  useThreshold(handleInfiniteScroll, 50);

  const LoadingSpinner = () => (
    <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-t-2 border-neutral-800" />
  );

  return (
    <div className="space-y-[10px] p-2">
      {agentLoading ? (
        <div className="flex h-[200px] items-center justify-center">
          <LoadingSpinner />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4">
            {agents?.map((agent) => (
              <LibraryAgentCard
                key={agent.id}
                id={agent.id}
                name={agent.name}
                isCreatedByUser={agent.isCreatedByUser}
                input_schema={agent.input_schema}
                output_schema={agent.output_schema}
                is_active={agent.is_active}
                version={agent.version}
                description={agent.description}
              />
            ))}
          </div>
          {loadingMore && (
            <div className="flex items-center justify-center py-4">
              <LoadingSpinner />
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default LibraryAgentListContainer;
