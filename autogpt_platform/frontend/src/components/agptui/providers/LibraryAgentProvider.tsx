import { GraphMeta, LibraryAgentFilterEnum } from "@/lib/autogpt-server-api";
import {
  createContext,
  useState,
  ReactNode,
  useContext,
  Dispatch,
  SetStateAction,
} from "react";

interface LibraryPageContextType {
  agents: GraphMeta[];
  setAgents: Dispatch<SetStateAction<GraphMeta[]>>;
  agentLoading: boolean;
  setAgentLoading: Dispatch<SetStateAction<boolean>>;
  searchTerm: string | undefined;
  setSearchTerm: Dispatch<SetStateAction<string | undefined>>;
  uploadedFile: File | null;
  setUploadedFile: Dispatch<SetStateAction<File | null>>;
  libraryFilter: LibraryAgentFilterEnum;
  setLibraryFilter: Dispatch<SetStateAction<LibraryAgentFilterEnum>>;
}

export const LibraryPageContext = createContext<LibraryPageContextType>(
  {} as LibraryPageContextType,
);

interface LibraryPageProviderProps {
  children: ReactNode;
}

export function LibraryPageProvider({ children }: LibraryPageProviderProps) {
  const [agents, setAgents] = useState<GraphMeta[]>([]);
  const [agentLoading, setAgentLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string | undefined>("");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [libraryFilter, setLibraryFilter] = useState<LibraryAgentFilterEnum>(
    LibraryAgentFilterEnum.UPDATED_AT,
  );

  return (
    <LibraryPageContext.Provider
      value={{
        agents,
        setAgents,
        agentLoading,
        setAgentLoading,
        searchTerm,
        setSearchTerm,
        uploadedFile,
        setUploadedFile,
        libraryFilter,
        setLibraryFilter,
      }}
    >
      {children}
    </LibraryPageContext.Provider>
  );
}

export function useLibraryPageContext(): LibraryPageContextType {
  const context = useContext(LibraryPageContext);
  if (!context) {
    throw new Error("Error in context of Library page");
  }
  return context;
}
