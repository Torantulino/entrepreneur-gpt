import BackendAPI from "./client";
import React, { createContext, useMemo } from "react";
import MockClient from "./mock_client";

const BackendAPIProviderContext = createContext<BackendAPI | null>(null);

interface BackendAPIProviderProps {
  children?: React.ReactNode;
  useMockBackend?: boolean;
}

export function BackendAPIProvider({
  children,
  useMockBackend,
}: BackendAPIProviderProps): React.ReactNode {
  let api: BackendAPI;

  if (useMockBackend) {
    api = useMemo(() => new MockClient(), []);
  } else {
    api = useMemo(() => new BackendAPI(), []);
  }

  return (
    <BackendAPIProviderContext.Provider value={api}>
      {children}
    </BackendAPIProviderContext.Provider>
  );
}

export function useBackendAPI(): BackendAPI {
  const context = React.useContext(BackendAPIProviderContext);
  if (!context) {
    throw new Error(
      "useBackendAPI must be used within a BackendAPIProviderContext",
    );
  }
  return context;
}
