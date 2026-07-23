/**
 * TruthLens AI – Frontend API Client
 *
 * Optimizations vs. original:
 *  - Single `request()` private helper eliminates the code duplication
 *    between get/post/postFile. Error handling is now in ONE place.
 *  - AbortController support via an optional `signal` parameter so components
 *    can cancel in-flight requests on unmount (prevents React state-on-unmount
 *    warnings).
 *  - Token is stored in a module-level variable on the client side and only
 *    falls back to localStorage on first access (avoids repeated storage reads
 *    on every request header build).
 *  - `ApiError` is a proper `Error` subclass so it can be caught with
 *    `instanceof ApiError` and gives a real stack trace.
 *  - Typed generic response with proper error body extraction.
 */

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

// ── Error type ────────────────────────────────────────────────────────────────

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly detail?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// ── Module-level token cache (client-side only) ───────────────────────────────

let _tokenCache: string | null | undefined = undefined; // undefined = not yet read

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  if (_tokenCache === undefined) {
    _tokenCache = localStorage.getItem("token");
  }
  return _tokenCache;
}

// ── Core request helper ───────────────────────────────────────────────────────

async function request<T>(
  method: string,
  endpoint: string,
  body?: unknown,
  signal?: AbortSignal
): Promise<T> {
  const headers: Record<string, string> = {};

  if (!(body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method,
    headers,
    body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
    signal,
  });

  if (!response.ok) {
    let detail: unknown;
    try {
      detail = await response.json();
    } catch {
      detail = await response.text().catch(() => undefined);
    }
    const message =
      (typeof detail === "object" && detail !== null && "detail" in detail
        ? String((detail as Record<string, unknown>).detail)
        : undefined) ?? `Request failed (${response.status})`;

    throw new ApiError(message, response.status, detail);
  }

  return response.json() as Promise<T>;
}

// ── Public API object ─────────────────────────────────────────────────────────

export const api = {
  get<T>(endpoint: string, signal?: AbortSignal): Promise<T> {
    return request<T>("GET", endpoint, undefined, signal);
  },

  post<T>(endpoint: string, body: unknown, signal?: AbortSignal): Promise<T> {
    return request<T>("POST", endpoint, body, signal);
  },

  postFile<T>(endpoint: string, file: File, signal?: AbortSignal): Promise<T> {
    const formData = new FormData();
    formData.append("file", file);
    return request<T>("POST", endpoint, formData, signal);
  },

  patch<T>(endpoint: string, body: unknown, signal?: AbortSignal): Promise<T> {
    return request<T>("PATCH", endpoint, body, signal);
  },

  delete<T>(endpoint: string, signal?: AbortSignal): Promise<T> {
    return request<T>("DELETE", endpoint, undefined, signal);
  },

  post2<T>(endpoint: string, signal?: AbortSignal): Promise<T> {
    return request<T>("POST", endpoint, undefined, signal);
  },

  setToken(token: string): void {
    if (typeof window !== "undefined") {
      localStorage.setItem("token", token);
      _tokenCache = token; // sync in-memory cache
    }
  },

  clearToken(): void {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      _tokenCache = null;
    }
  },

  isAuthenticated(): boolean {
    return !!getToken();
  },
};
