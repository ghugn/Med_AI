import { config } from "@/config";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

interface RequestOptions<TBody = unknown> {
  method?: HttpMethod;
  body?: TBody;
  headers?: Record<string, string>;
  /** AbortController signal for cancellation */
  signal?: AbortSignal;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<TResponse, TBody = unknown>(
  path: string,
  options: RequestOptions<TBody> = {}
): Promise<TResponse> {
  const { method = "GET", body, headers = {}, signal } = options;

  const url = path.startsWith("http") ? path : `${config.apiBaseUrl}${path}`;

  const res = await fetch(url, {
    method,
    signal,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new ApiError(res.status, res.statusText, text);
  }

  return res.json() as Promise<TResponse>;
}

export const apiClient = {
  get: <T>(path: string, opts?: Omit<RequestOptions, "method" | "body">) =>
    request<T>(path, { ...opts, method: "GET" }),

  post: <T, B = unknown>(path: string, body: B, opts?: Omit<RequestOptions<B>, "method" | "body">) =>
    request<T, B>(path, { ...opts, method: "POST", body }),
};
