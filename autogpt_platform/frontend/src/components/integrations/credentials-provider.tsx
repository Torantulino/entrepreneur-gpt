import {
  APIKeyCredentials,
  CredentialsDeleteNeedConfirmationResponse,
  CredentialsDeleteResponse,
  CredentialsMetaResponse,
  CredentialsProviderName,
  PROVIDER_NAMES,
  UserPasswordCredentials,
} from "@/lib/autogpt-server-api";
import { useBackendAPI } from "@/lib/autogpt-server-api/context";
import { createContext, useCallback, useEffect, useState } from "react";

// Get keys from CredentialsProviderName type
const CREDENTIALS_PROVIDER_NAMES = Object.values(
  PROVIDER_NAMES,
) as CredentialsProviderName[];

// --8<-- [start:CredentialsProviderNames]
const providerDisplayNames: Record<CredentialsProviderName, string> = {
  anthropic: "Anthropic",
  apollo: "Apollo",
  discord: "Discord",
  d_id: "D-ID",
  e2b: "E2B",
  exa: "Exa",
  fal: "FAL",
  github: "GitHub",
  google: "Google",
  google_maps: "Google Maps",
  groq: "Groq",
  hubspot: "Hubspot",
  ideogram: "Ideogram",
  jina: "Jina",
  linear: "Linear",
  medium: "Medium",
  mem0: "Mem0",
  notion: "Notion",
  nvidia: "Nvidia",
  ollama: "Ollama",
  openai: "OpenAI",
  openweathermap: "OpenWeatherMap",
  open_router: "Open Router",
  pinecone: "Pinecone",
  screenshotone: "ScreenshotOne",
  slant3d: "Slant3D",
  smartlead: "SmartLead",
  smtp: "SMTP",
  reddit: "Reddit",
  replicate: "Replicate",
  revid: "Rev.ID",
  twitter: "Twitter",
  todoist: "Todoist",
  unreal_speech: "Unreal Speech",
  zerobounce: "ZeroBounce",
} as const;
// --8<-- [end:CredentialsProviderNames]

type APIKeyCredentialsCreatable = Omit<
  APIKeyCredentials,
  "id" | "provider" | "type"
>;

type UserPasswordCredentialsCreatable = Omit<
  UserPasswordCredentials,
  "id" | "provider" | "type"
>;

export type CredentialsProviderData = {
  provider: CredentialsProviderName;
  providerName: string;
  savedApiKeys: CredentialsMetaResponse[];
  savedOAuthCredentials: CredentialsMetaResponse[];
  savedUserPasswordCredentials: CredentialsMetaResponse[];
  oAuthCallback: (
    code: string,
    state_token: string,
  ) => Promise<CredentialsMetaResponse>;
  createAPIKeyCredentials: (
    credentials: APIKeyCredentialsCreatable,
  ) => Promise<CredentialsMetaResponse>;
  createUserPasswordCredentials: (
    credentials: UserPasswordCredentialsCreatable,
  ) => Promise<CredentialsMetaResponse>;
  deleteCredentials: (
    id: string,
    force?: boolean,
  ) => Promise<
    CredentialsDeleteResponse | CredentialsDeleteNeedConfirmationResponse
  >;
};

export type CredentialsProvidersContextType = {
  [key in CredentialsProviderName]?: CredentialsProviderData;
};

export const CredentialsProvidersContext =
  createContext<CredentialsProvidersContextType | null>(null);

export default function CredentialsProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [providers, setProviders] =
    useState<CredentialsProvidersContextType | null>(null);
  const api = useBackendAPI();

  const addCredentials = useCallback(
    (
      provider: CredentialsProviderName,
      credentials: CredentialsMetaResponse,
    ) => {
      setProviders((prev) => {
        if (!prev || !prev[provider]) return prev;

        const updatedProvider = { ...prev[provider] };

        if (credentials.type === "api_key") {
          updatedProvider.savedApiKeys = [
            ...updatedProvider.savedApiKeys,
            credentials,
          ];
        } else if (credentials.type === "oauth2") {
          updatedProvider.savedOAuthCredentials = [
            ...updatedProvider.savedOAuthCredentials,
            credentials,
          ];
        } else if (credentials.type === "user_password") {
          updatedProvider.savedUserPasswordCredentials = [
            ...updatedProvider.savedUserPasswordCredentials,
            credentials,
          ];
        }

        return {
          ...prev,
          [provider]: updatedProvider,
        };
      });
    },
    [setProviders],
  );

  /** Wraps `BackendAPI.oAuthCallback`, and adds the result to the internal credentials store. */
  const oAuthCallback = useCallback(
    async (
      provider: CredentialsProviderName,
      code: string,
      state_token: string,
    ): Promise<CredentialsMetaResponse> => {
      const credsMeta = await api.oAuthCallback(provider, code, state_token);
      addCredentials(provider, credsMeta);
      return credsMeta;
    },
    [api, addCredentials],
  );

  /** Wraps `BackendAPI.createAPIKeyCredentials`, and adds the result to the internal credentials store. */
  const createAPIKeyCredentials = useCallback(
    async (
      provider: CredentialsProviderName,
      credentials: APIKeyCredentialsCreatable,
    ): Promise<CredentialsMetaResponse> => {
      const credsMeta = await api.createAPIKeyCredentials({
        provider,
        ...credentials,
      });
      addCredentials(provider, credsMeta);
      return credsMeta;
    },
    [api, addCredentials],
  );

  /** Wraps `BackendAPI.createUserPasswordCredentials`, and adds the result to the internal credentials store. */
  const createUserPasswordCredentials = useCallback(
    async (
      provider: CredentialsProviderName,
      credentials: UserPasswordCredentialsCreatable,
    ): Promise<CredentialsMetaResponse> => {
      const credsMeta = await api.createUserPasswordCredentials({
        provider,
        ...credentials,
      });
      addCredentials(provider, credsMeta);
      return credsMeta;
    },
    [api, addCredentials],
  );

  /** Wraps `BackendAPI.deleteCredentials`, and removes the credentials from the internal store. */
  const deleteCredentials = useCallback(
    async (
      provider: CredentialsProviderName,
      id: string,
      force: boolean = false,
    ): Promise<
      CredentialsDeleteResponse | CredentialsDeleteNeedConfirmationResponse
    > => {
      const result = await api.deleteCredentials(provider, id, force);
      if (!result.deleted) {
        return result;
      }
      setProviders((prev) => {
        if (!prev || !prev[provider]) return prev;

        const updatedProvider = { ...prev[provider] };
        updatedProvider.savedApiKeys = updatedProvider.savedApiKeys.filter(
          (cred) => cred.id !== id,
        );
        updatedProvider.savedOAuthCredentials =
          updatedProvider.savedOAuthCredentials.filter(
            (cred) => cred.id !== id,
          );
        updatedProvider.savedUserPasswordCredentials =
          updatedProvider.savedUserPasswordCredentials.filter(
            (cred) => cred.id !== id,
          );
        return {
          ...prev,
          [provider]: updatedProvider,
        };
      });
      return result;
    },
    [api],
  );

  useEffect(() => {
    api.isAuthenticated().then((isAuthenticated) => {
      if (!isAuthenticated) return;

      api.listCredentials().then((response) => {
        const credentialsByProvider = response.reduce(
          (acc, cred) => {
            if (!acc[cred.provider]) {
              acc[cred.provider] = {
                oauthCreds: [],
                apiKeys: [],
                userPasswordCreds: [],
              };
            }
            if (cred.type === "oauth2") {
              acc[cred.provider].oauthCreds.push(cred);
            } else if (cred.type === "api_key") {
              acc[cred.provider].apiKeys.push(cred);
            } else if (cred.type === "user_password") {
              acc[cred.provider].userPasswordCreds.push(cred);
            }
            return acc;
          },
          {} as Record<
            CredentialsProviderName,
            {
              oauthCreds: CredentialsMetaResponse[];
              apiKeys: CredentialsMetaResponse[];
              userPasswordCreds: CredentialsMetaResponse[];
            }
          >,
        );

        setProviders((prev) => ({
          ...prev,
          ...Object.fromEntries(
            CREDENTIALS_PROVIDER_NAMES.map((provider) => [
              provider,
              {
                provider,
                providerName:
                  providerDisplayNames[provider as CredentialsProviderName],
                savedApiKeys: credentialsByProvider[provider]?.apiKeys ?? [],
                savedOAuthCredentials:
                  credentialsByProvider[provider]?.oauthCreds ?? [],
                savedUserPasswordCredentials:
                  credentialsByProvider[provider]?.userPasswordCreds ?? [],
                oAuthCallback: (code: string, state_token: string) =>
                  oAuthCallback(
                    provider as CredentialsProviderName,
                    code,
                    state_token,
                  ),
                createAPIKeyCredentials: (
                  credentials: APIKeyCredentialsCreatable,
                ) =>
                  createAPIKeyCredentials(
                    provider as CredentialsProviderName,
                    credentials,
                  ),
                createUserPasswordCredentials: (
                  credentials: UserPasswordCredentialsCreatable,
                ) =>
                  createUserPasswordCredentials(
                    provider as CredentialsProviderName,
                    credentials,
                  ),
                deleteCredentials: (id: string, force: boolean = false) =>
                  deleteCredentials(
                    provider as CredentialsProviderName,
                    id,
                    force,
                  ),
              },
            ]),
          ),
        }));
      });
    });
  }, [
    api,
    createAPIKeyCredentials,
    createUserPasswordCredentials,
    deleteCredentials,
    oAuthCallback,
  ]);

  return (
    <CredentialsProvidersContext.Provider value={providers}>
      {children}
    </CredentialsProvidersContext.Provider>
  );
}
