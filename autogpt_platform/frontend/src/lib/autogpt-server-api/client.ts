import { SupabaseClient } from "@supabase/supabase-js";
import {
  AnalyticsDetails,
  AnalyticsMetrics,
  APIKey,
  APIKeyCredentials,
  APIKeyPermission,
  Block,
  CreatorsResponse,
  CreatorDetails,
  CreateAPIKeyResponse,
  Credentials,
  CredentialsDeleteNeedConfirmationResponse,
  CredentialsDeleteResponse,
  CredentialsMetaResponse,
  GraphExecution,
  Graph,
  GraphCreatable,
  GraphMeta,
  GraphUpdateable,
  MyAgentsResponse,
  NodeExecutionResult,
  ProfileDetails,
  Schedule,
  ScheduleCreatable,
  StoreAgentsResponse,
  StoreAgentDetails,
  StoreSubmissionsResponse,
  StoreSubmissionRequest,
  StoreSubmission,
  StoreReviewCreate,
  StoreReview,
  TransactionHistory,
  User,
  UserPasswordCredentials,
} from "./types";
import { createBrowserClient } from "@supabase/ssr";
import getServerSupabase from "../supabase/getServerSupabase";

const isClient = typeof window !== "undefined";

export default class BackendAPI {
  private baseUrl: string;
  private wsUrl: string;
  private webSocket: WebSocket | null = null;
  private wsConnecting: Promise<void> | null = null;
  private wsMessageHandlers: Record<string, Set<(data: any) => void>> = {};
  heartbeatInterval: number | null = null;
  readonly HEARTBEAT_INTERVAL = 10_0000; // 100 seconds
  readonly HEARTBEAT_TIMEOUT = 10_000; // 10 seconds
  heartbeatTimeoutId: number | null = null;

  constructor(
    baseUrl: string = process.env.NEXT_PUBLIC_AGPT_SERVER_URL ||
      "http://localhost:8006/api",
    wsUrl: string = process.env.NEXT_PUBLIC_AGPT_WS_SERVER_URL ||
      "ws://localhost:8001/ws",
  ) {
    this.baseUrl = baseUrl;
    this.wsUrl = wsUrl;
  }

  private get supabaseClient(): SupabaseClient | null {
    return isClient
      ? createBrowserClient(
          process.env.NEXT_PUBLIC_SUPABASE_URL!,
          process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        )
      : getServerSupabase();
  }

  async isAuthenticated(): Promise<boolean> {
    if (!this.supabaseClient) return false;
    const {
      data: { user },
    } = await this.supabaseClient?.auth.getUser();
    return user != null;
  }

  createUser(): Promise<User> {
    return this._request("POST", "/auth/user", {});
  }

  getUserCredit(page?: string): Promise<{ credits: number }> {
    try {
      return this._get(`/credits`, undefined, page);
    } catch (error) {
      return Promise.resolve({ credits: 0 });
    }
  }

  getAutoTopUpConfig(): Promise<{ amount: number; threshold: number }> {
    return this._get("/credits/auto-top-up");
  }

  setAutoTopUpConfig(config: {
    amount: number;
    threshold: number;
  }): Promise<{ amount: number; threshold: number }> {
    return this._request("POST", "/credits/auto-top-up", config);
  }

  getTransactionHistory(
    lastTransction: Date | null,
    countLimit: number,
  ): Promise<TransactionHistory> {
    return this._get(
      `/credits/transactions`,
      lastTransction
        ? {
            transaction_time: lastTransction,
            transaction_count_limit: countLimit,
          }
        : {
            transaction_count_limit: countLimit,
          },
    );
  }

  requestTopUp(credit_amount: number): Promise<{ checkout_url: string }> {
    return this._request("POST", "/credits", { credit_amount });
  }

  getUserPaymentPortalLink(): Promise<{ url: string }> {
    return this._get("/credits/manage");
  }

  fulfillCheckout(): Promise<void> {
    return this._request("PATCH", "/credits");
  }

  getBlocks(): Promise<Block[]> {
    return this._get("/blocks");
  }

  listGraphs(): Promise<GraphMeta[]> {
    return this._get(`/graphs`);
  }

  getExecutions(): Promise<GraphExecution[]> {
    return this._get(`/executions`);
  }

  getGraph(
    id: string,
    version?: number,
    hide_credentials?: boolean,
  ): Promise<Graph> {
    let query: Record<string, any> = {};
    if (version !== undefined) {
      query["version"] = version;
    }
    if (hide_credentials !== undefined) {
      query["hide_credentials"] = hide_credentials;
    }
    return this._get(`/graphs/${id}`, query);
  }

  getGraphAllVersions(id: string): Promise<Graph[]> {
    return this._get(`/graphs/${id}/versions`);
  }

  createGraph(graphCreateBody: GraphCreatable): Promise<Graph>;

  createGraph(graphID: GraphCreatable | string): Promise<Graph> {
    let requestBody = { graph: graphID } as GraphCreateRequestBody;

    return this._request("POST", "/graphs", requestBody);
  }

  updateGraph(id: string, graph: GraphUpdateable): Promise<Graph> {
    return this._request("PUT", `/graphs/${id}`, graph);
  }

  deleteGraph(id: string): Promise<void> {
    return this._request("DELETE", `/graphs/${id}`);
  }

  setGraphActiveVersion(id: string, version: number): Promise<Graph> {
    return this._request("PUT", `/graphs/${id}/versions/active`, {
      active_graph_version: version,
    });
  }

  executeGraph(
    id: string,
    version: number,
    inputData: { [key: string]: any } = {},
  ): Promise<{ graph_exec_id: string }> {
    return this._request("POST", `/graphs/${id}/execute/${version}`, inputData);
  }

  async getGraphExecutionInfo(
    graphID: string,
    runID: string,
  ): Promise<NodeExecutionResult[]> {
    return (await this._get(`/graphs/${graphID}/executions/${runID}`)).map(
      parseNodeExecutionResultTimestamps,
    );
  }

  async stopGraphExecution(
    graphID: string,
    runID: string,
  ): Promise<NodeExecutionResult[]> {
    return (
      await this._request("POST", `/graphs/${graphID}/executions/${runID}/stop`)
    ).map(parseNodeExecutionResultTimestamps);
  }

  oAuthLogin(
    provider: string,
    scopes?: string[],
  ): Promise<{ login_url: string; state_token: string }> {
    const query = scopes ? { scopes: scopes.join(",") } : undefined;
    return this._get(`/integrations/${provider}/login`, query);
  }

  oAuthCallback(
    provider: string,
    code: string,
    state_token: string,
  ): Promise<CredentialsMetaResponse> {
    return this._request("POST", `/integrations/${provider}/callback`, {
      code,
      state_token,
    });
  }

  createAPIKeyCredentials(
    credentials: Omit<APIKeyCredentials, "id" | "type">,
  ): Promise<APIKeyCredentials> {
    return this._request(
      "POST",
      `/integrations/${credentials.provider}/credentials`,
      { ...credentials, type: "api_key" },
    );
  }

  createUserPasswordCredentials(
    credentials: Omit<UserPasswordCredentials, "id" | "type">,
  ): Promise<UserPasswordCredentials> {
    return this._request(
      "POST",
      `/integrations/${credentials.provider}/credentials`,
      { ...credentials, type: "user_password" },
    );
  }

  listCredentials(provider?: string): Promise<CredentialsMetaResponse[]> {
    return this._get(
      provider
        ? `/integrations/${provider}/credentials`
        : "/integrations/credentials",
    );
  }

  getCredentials(provider: string, id: string): Promise<Credentials> {
    return this._get(`/integrations/${provider}/credentials/${id}`);
  }

  deleteCredentials(
    provider: string,
    id: string,
    force: boolean = true,
  ): Promise<
    CredentialsDeleteResponse | CredentialsDeleteNeedConfirmationResponse
  > {
    return this._request(
      "DELETE",
      `/integrations/${provider}/credentials/${id}`,
      force ? { force: true } : undefined,
    );
  }

  // API Key related requests
  async createAPIKey(
    name: string,
    permissions: APIKeyPermission[],
    description?: string,
  ): Promise<CreateAPIKeyResponse> {
    return this._request("POST", "/api-keys", {
      name,
      permissions,
      description,
    });
  }

  async listAPIKeys(): Promise<APIKey[]> {
    return this._get("/api-keys");
  }

  async revokeAPIKey(keyId: string): Promise<APIKey> {
    return this._request("DELETE", `/api-keys/${keyId}`);
  }

  async updateAPIKeyPermissions(
    keyId: string,
    permissions: APIKeyPermission[],
  ): Promise<APIKey> {
    return this._request("PUT", `/api-keys/${keyId}/permissions`, {
      permissions,
    });
  }

  /**
   * @returns `true` if a ping event was received, `false` if provider doesn't support pinging but the webhook exists.
   * @throws  `Error` if the webhook does not exist.
   * @throws  `Error` if the attempt to ping timed out.
   */
  async pingWebhook(webhook_id: string): Promise<boolean> {
    return this._request("POST", `/integrations/webhooks/${webhook_id}/ping`);
  }

  logMetric(metric: AnalyticsMetrics) {
    return this._request("POST", "/analytics/log_raw_metric", metric);
  }

  logAnalytic(analytic: AnalyticsDetails) {
    return this._request("POST", "/analytics/log_raw_analytics", analytic);
  }

  ///////////////////////////////////////////
  /////////// V2 STORE API /////////////////
  /////////////////////////////////////////

  getStoreProfile(page?: string): Promise<ProfileDetails | null> {
    try {
      console.log("+++ Making API from: ", page);
      const result = this._get("/store/profile", undefined, page);
      return result;
    } catch (error) {
      console.error("Error fetching store profile:", error);
      return Promise.resolve(null);
    }
  }

  getStoreAgents(params?: {
    featured?: boolean;
    creator?: string;
    sorted_by?: string;
    search_query?: string;
    category?: string;
    page?: number;
    page_size?: number;
  }): Promise<StoreAgentsResponse> {
    return this._get("/store/agents", params);
  }

  getStoreAgent(
    username: string,
    agentName: string,
  ): Promise<StoreAgentDetails> {
    return this._get(
      `/store/agents/${encodeURIComponent(username)}/${encodeURIComponent(
        agentName,
      )}`,
    );
  }

  getStoreCreators(params?: {
    featured?: boolean;
    search_query?: string;
    sorted_by?: string;
    page?: number;
    page_size?: number;
  }): Promise<CreatorsResponse> {
    return this._get("/store/creators", params);
  }

  getStoreCreator(username: string): Promise<CreatorDetails> {
    return this._get(`/store/creator/${encodeURIComponent(username)}`);
  }

  getStoreSubmissions(params?: {
    page?: number;
    page_size?: number;
  }): Promise<StoreSubmissionsResponse> {
    return this._get("/store/submissions", params);
  }

  createStoreSubmission(
    submission: StoreSubmissionRequest,
  ): Promise<StoreSubmission> {
    return this._request("POST", "/store/submissions", submission);
  }

  generateStoreSubmissionImage(
    agent_id: string,
  ): Promise<{ image_url: string }> {
    return this._request(
      "POST",
      "/store/submissions/generate_image?agent_id=" + agent_id,
    );
  }

  deleteStoreSubmission(submission_id: string): Promise<boolean> {
    return this._request("DELETE", `/store/submissions/${submission_id}`);
  }

  uploadStoreSubmissionMedia(file: File): Promise<string> {
    const formData = new FormData();
    formData.append("file", file);
    return this._uploadFile("/store/submissions/media", file);
  }

  updateStoreProfile(profile: ProfileDetails): Promise<ProfileDetails> {
    return this._request("POST", "/store/profile", profile);
  }

  reviewAgent(
    username: string,
    agentName: string,
    review: StoreReviewCreate,
  ): Promise<StoreReview> {
    console.log("Reviewing agent: ", username, agentName, review);
    return this._request(
      "POST",
      `/store/agents/${encodeURIComponent(username)}/${encodeURIComponent(
        agentName,
      )}/review`,
      review,
    );
  }

  getMyAgents(params?: {
    page?: number;
    page_size?: number;
  }): Promise<MyAgentsResponse> {
    return this._get("/store/myagents", params);
  }

  downloadStoreAgent(
    storeListingVersionId: string,
    version?: number,
  ): Promise<BlobPart> {
    const url = version
      ? `/store/download/agents/${storeListingVersionId}?version=${version}`
      : `/store/download/agents/${storeListingVersionId}`;

    return this._get(url);
  }

  /////////////////////////////////////////
  /////////// V2 LIBRARY API //////////////
  /////////////////////////////////////////

  async listLibraryAgents(): Promise<GraphMeta[]> {
    return this._get("/library/agents");
  }

  async addAgentToLibrary(storeListingVersionId: string): Promise<void> {
    await this._request("POST", `/library/agents/${storeListingVersionId}`);
  }

  ///////////////////////////////////////////
  /////////// INTERNAL FUNCTIONS ////////////
  //////////////////////////////??///////////

  private async _get(path: string, query?: Record<string, any>, page?: string) {
    return this._request("GET", path, query, page);
  }

  async createSchedule(schedule: ScheduleCreatable): Promise<Schedule> {
    return this._request("POST", `/schedules`, schedule);
  }

  async deleteSchedule(scheduleId: string): Promise<Schedule> {
    return this._request("DELETE", `/schedules/${scheduleId}`);
  }

  async listSchedules(): Promise<Schedule[]> {
    return this._get(`/schedules`);
  }

  private async _uploadFile(path: string, file: File): Promise<string> {
    // Get session with retry logic
    let token = "no-token-found";
    let retryCount = 0;
    const maxRetries = 3;

    while (retryCount < maxRetries) {
      const {
        data: { session },
      } = (await this.supabaseClient?.auth.getSession()) || {
        data: { session: null },
      };

      if (session?.access_token) {
        token = session.access_token;
        break;
      }

      retryCount++;
      if (retryCount < maxRetries) {
        await new Promise((resolve) => setTimeout(resolve, 100 * retryCount));
      }
    }

    // Create a FormData object and append the file
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(this.baseUrl + path, {
      method: "POST",
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Error uploading file: ${response.statusText}`);
    }

    // Parse the response appropriately
    const media_url = await response.text();
    return media_url;
  }

  private async _request(
    method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE",
    path: string,
    payload?: Record<string, any>,
    page?: string,
  ) {
    if (method !== "GET") {
      console.debug(`${method} ${path} payload:`, payload);
    }

    // Get session with retry logic
    let token = "no-token-found";
    let retryCount = 0;
    const maxRetries = 3;

    while (retryCount < maxRetries) {
      const {
        data: { session },
      } = (await this.supabaseClient?.auth.getSession()) || {
        data: { session: null },
      };

      if (session?.access_token) {
        token = session.access_token;
        break;
      }

      retryCount++;
      if (retryCount < maxRetries) {
        await new Promise((resolve) => setTimeout(resolve, 100 * retryCount));
      }
    }

    let url = this.baseUrl + path;
    const payloadAsQuery = ["GET", "DELETE"].includes(method);
    if (payloadAsQuery && payload) {
      // For GET requests, use payload as query
      const queryParams = new URLSearchParams(payload);
      url += `?${queryParams.toString()}`;
    }

    const hasRequestBody = !payloadAsQuery && payload !== undefined;
    const response = await fetch(url, {
      method,
      headers: {
        ...(hasRequestBody && { "Content-Type": "application/json" }),
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: hasRequestBody ? JSON.stringify(payload) : undefined,
    });

    if (!response.ok) {
      console.warn(`${method} ${path} returned non-OK response:`, response);

      // console.warn("baseClient is attempting to redirect by changing window location")
      // if (
      //   response.status === 403 &&
      //   response.statusText === "Not authenticated" &&
      //   typeof window !== "undefined" // Check if in browser environment
      // ) {
      //   window.location.href = "/login";
      // }

      let errorDetail;
      try {
        const errorData = await response.json();
        if (
          Array.isArray(errorData.detail) &&
          errorData.detail.length > 0 &&
          errorData.detail[0].loc
        ) {
          // This appears to be a Pydantic validation error
          const errors = errorData.detail.map(
            (err: _PydanticValidationError) => {
              const location = err.loc.join(" -> ");
              return `${location}: ${err.msg}`;
            },
          );
          errorDetail = errors.join("\n");
        } else {
          errorDetail = errorData.detail || response.statusText;
        }
      } catch (e) {
        errorDetail = response.statusText;
      }

      throw new Error(errorDetail);
    }

    // Handle responses with no content (like DELETE requests)
    if (
      response.status === 204 ||
      response.headers.get("Content-Length") === "0"
    ) {
      return null;
    }

    try {
      return await response.json();
    } catch (e) {
      if (e instanceof SyntaxError) {
        console.warn(`${method} ${path} returned invalid JSON:`, e);
        return null;
      }
      throw e;
    }
  }

  startHeartbeat() {
    this.stopHeartbeat();
    this.heartbeatInterval = window.setInterval(() => {
      if (this.webSocket?.readyState === WebSocket.OPEN) {
        this.webSocket.send(
          JSON.stringify({
            method: "heartbeat",
            data: "ping",
            success: true,
          }),
        );

        this.heartbeatTimeoutId = window.setTimeout(() => {
          console.log("Heartbeat timeout - reconnecting");
          this.webSocket?.close();
          this.connectWebSocket();
        }, this.HEARTBEAT_TIMEOUT);
      }
    }, this.HEARTBEAT_INTERVAL);
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
    if (this.heartbeatTimeoutId) {
      clearTimeout(this.heartbeatTimeoutId);
      this.heartbeatTimeoutId = null;
    }
  }

  handleHeartbeatResponse() {
    if (this.heartbeatTimeoutId) {
      clearTimeout(this.heartbeatTimeoutId);
      this.heartbeatTimeoutId = null;
    }
  }

  async connectWebSocket(): Promise<void> {
    this.wsConnecting ??= new Promise(async (resolve, reject) => {
      try {
        const token =
          (await this.supabaseClient?.auth.getSession())?.data.session
            ?.access_token || "";
        const wsUrlWithToken = `${this.wsUrl}?token=${token}`;
        this.webSocket = new WebSocket(wsUrlWithToken);

        this.webSocket.onopen = () => {
          console.log("WebSocket connection established");
          this.startHeartbeat(); // Start heartbeat when connection opens
          resolve();
        };

        this.webSocket.onclose = (event) => {
          console.log("WebSocket connection closed", event);
          this.stopHeartbeat(); // Stop heartbeat when connection closes
          this.webSocket = null;
          // Attempt to reconnect after a delay
          setTimeout(() => this.connectWebSocket(), 1000);
        };

        this.webSocket.onerror = (error) => {
          console.error("WebSocket error:", error);
          this.stopHeartbeat(); // Stop heartbeat on error
          reject(error);
        };

        this.webSocket.onmessage = (event) => {
          const message: WebsocketMessage = JSON.parse(event.data);

          // Handle heartbeat response
          if (message.method === "heartbeat" && message.data === "pong") {
            this.handleHeartbeatResponse();
            return;
          }

          if (message.method === "execution_event") {
            message.data = parseNodeExecutionResultTimestamps(message.data);
          }
          this.wsMessageHandlers[message.method]?.forEach((handler) =>
            handler(message.data),
          );
        };
      } catch (error) {
        console.error("Error connecting to WebSocket:", error);
        reject(error);
      }
    });
    return this.wsConnecting;
  }

  disconnectWebSocket() {
    this.stopHeartbeat(); // Stop heartbeat when disconnecting
    if (this.webSocket && this.webSocket.readyState === WebSocket.OPEN) {
      this.webSocket.close();
    }
  }

  sendWebSocketMessage<M extends keyof WebsocketMessageTypeMap>(
    method: M,
    data: WebsocketMessageTypeMap[M],
    callCount = 0,
  ) {
    if (this.webSocket && this.webSocket.readyState === WebSocket.OPEN) {
      this.webSocket.send(JSON.stringify({ method, data }));
    } else {
      this.connectWebSocket().then(() => {
        callCount == 0
          ? this.sendWebSocketMessage(method, data, callCount + 1)
          : setTimeout(
              () => {
                this.sendWebSocketMessage(method, data, callCount + 1);
              },
              2 ** (callCount - 1) * 1000,
            );
      });
    }
  }

  onWebSocketMessage<M extends keyof WebsocketMessageTypeMap>(
    method: M,
    handler: (data: WebsocketMessageTypeMap[M]) => void,
  ): () => void {
    this.wsMessageHandlers[method] ??= new Set();
    this.wsMessageHandlers[method].add(handler);

    // Return detacher
    return () => this.wsMessageHandlers[method].delete(handler);
  }

  subscribeToExecution(graphId: string, graphVersion: number) {
    this.sendWebSocketMessage("subscribe", {
      graph_id: graphId,
      graph_version: graphVersion,
    });
  }
}

/* *** UTILITY TYPES *** */

type GraphCreateRequestBody = {
  graph: GraphCreatable;
};

type WebsocketMessageTypeMap = {
  subscribe: { graph_id: string; graph_version: number };
  execution_event: NodeExecutionResult;
  heartbeat: "ping" | "pong";
};

type WebsocketMessage = {
  [M in keyof WebsocketMessageTypeMap]: {
    method: M;
    data: WebsocketMessageTypeMap[M];
  };
}[keyof WebsocketMessageTypeMap];

type _PydanticValidationError = {
  type: string;
  loc: string[];
  msg: string;
  input: any;
};

/* *** HELPER FUNCTIONS *** */

function parseNodeExecutionResultTimestamps(result: any): NodeExecutionResult {
  return {
    ...result,
    add_time: new Date(result.add_time),
    queue_time: result.queue_time ? new Date(result.queue_time) : undefined,
    start_time: result.start_time ? new Date(result.start_time) : undefined,
    end_time: result.end_time ? new Date(result.end_time) : undefined,
  };
}
