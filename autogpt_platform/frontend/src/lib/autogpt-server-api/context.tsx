import BackendAPI from "./client";
import React, { createContext, useMemo } from "react";
import MockClient, { MockClientProps } from "./mock_client";

const BackendAPIProviderContext = createContext<BackendAPI | null>(null);

interface BackendAPIProviderProps {
  children?: React.ReactNode;
  useMockBackend?: boolean;
  mockClientProps?: MockClientProps;
}

export function BackendAPIProvider({
  children,
  useMockBackend,
  mockClientProps,
}: BackendAPIProviderProps): React.ReactNode {
  const api = useMemo(() => {
    if (useMockBackend) {
      return new MockClient(mockClientProps);
    }
    return new BackendAPI();
  }, [useMockBackend, mockClientProps]);

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
