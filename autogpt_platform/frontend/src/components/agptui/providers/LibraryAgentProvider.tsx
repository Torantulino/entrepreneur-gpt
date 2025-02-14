import { LibraryAgent, LibraryAgentSortEnum } from "@/lib/autogpt-server-api";
import {
  createContext,
  useState,
  ReactNode,
  useContext,
  Dispatch,
  SetStateAction,
} from "react";

interface LibraryPageContextType {
  agents: LibraryAgent[];
  setAgents: Dispatch<SetStateAction<LibraryAgent[]>>;
  agentLoading: boolean;
  setAgentLoading: Dispatch<SetStateAction<boolean>>;
  searchTerm: string | undefined;
  setSearchTerm: Dispatch<SetStateAction<string | undefined>>;
  uploadedFile: File | null;
  setUploadedFile: Dispatch<SetStateAction<File | null>>;
  librarySort: LibraryAgentSortEnum;
  setLibrarySort: Dispatch<SetStateAction<LibraryAgentSortEnum>>;
}

export const LibraryPageContext = createContext<LibraryPageContextType>(
  {} as LibraryPageContextType,
);

interface LibraryPageProviderProps {
  children: ReactNode;
}

export function LibraryPageProvider({ children }: LibraryPageProviderProps) {
  const [agents, setAgents] = useState<LibraryAgent[]>([]);
  const [agentLoading, setAgentLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string | undefined>("");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [librarySort, setLibrarySort] = useState<LibraryAgentSortEnum>(
    LibraryAgentSortEnum.UPDATED_AT,
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
        librarySort,
        setLibrarySort,
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
