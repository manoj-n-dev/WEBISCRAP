import { playInterfaceSound } from "@/lib/useSound";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" && window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1"
    ? "https://webiscrap-api.onrender.com"
    : "http://localhost:8000");

/**
 * Cookie-bearing auth endpoints go through the SAME-ORIGIN Next.js rewrite (/api/auth/* -> backend) so the refresh cookie is a
 * first-party cookie. A cross-site cookie (vercel.app -> onrender.com) is blocked by Safari/iOS, Brave, Firefox strict mode and
 * Chrome incognito, which logged people (and guests) out on every reload. Set NEXT_PUBLIC_AUTH_PROXY=false to disable.
 */
const AUTH_PROXY = process.env.NEXT_PUBLIC_AUTH_PROXY !== "false";

function urlFor(endpoint: string): string {
  if (AUTH_PROXY && typeof window !== "undefined" && endpoint.startsWith("/api/auth/")) return endpoint;
  return `${API_BASE_URL}${endpoint}`;
}

export class ApiError extends Error {
  status: number;
  code?: string;
  detail?: unknown;
  retryAfter?: number;
  scope?: string;
  constructor(message: string, status: number, extra: Partial<ApiError> = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    Object.assign(this, extra);
  }
}

// In-memory access token storage (immune to localStorage XSS attacks)
let accessToken: string | null = null;

// Single-flight refresh lock: concurrent 401s share ONE refresh request instead of revoking each other's rotated token
let refreshPromise: Promise<string | null> | null = null;

async function performSilentRefresh(): Promise<string | null> {
  if (refreshPromise) return refreshPromise;
  refreshPromise = (async () => {
    try {
      const res = await fetch(urlFor("/api/auth/refresh"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
      });
      if (res.ok) {
        const data = await res.json();
        accessToken = data.access_token;
        return data.access_token as string;
      }
    } catch {
      // not authenticated
    }
    return null;
  })().finally(() => {
    refreshPromise = null;
  });
  return refreshPromise;
}

async function fetchWithTimeout(input: string, init: RequestInit, timeoutMs: number): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(input, { ...init, signal: controller.signal });
  } catch (e) {
    if ((e as Error)?.name === "AbortError") {
      throw new ApiError("The server is taking too long to respond (it may be waking up). Please try again in a moment.", 0, { code: "TIMEOUT" });
    }
    throw new ApiError("Can't reach the server. Check your connection and try again.", 0, { code: "NETWORK" });
  } finally {
    clearTimeout(timer);
  }
}

async function toApiError(response: Response): Promise<ApiError> {
  const body = await response.json().catch(() => ({} as Record<string, unknown>));
  const detail = (body as { detail?: unknown }).detail;
  let message = `Request failed (${response.status})`;
  const extra: Partial<ApiError> = { detail };
  if (typeof detail === "string") {
    message = detail;
  } else if (Array.isArray(detail)) {
    message = detail.map((d: { msg?: string }) => d?.msg).filter(Boolean).join(", ") || message;
  } else if (detail && typeof detail === "object") {
    const d = detail as { code?: string; message?: string; retry_after?: number; scope?: string };
    message = d.message || message;
    extra.code = d.code;
    extra.retryAfter = d.retry_after ?? undefined;
    extra.scope = d.scope ?? undefined;
  }
  if (response.status === 429 && !extra.code) {
    extra.code = "RATE_LIMIT";
    extra.retryAfter = Number(response.headers.get("retry-after")) || undefined;
  }
  return new ApiError(message, response.status, extra);
}

type ReqOpts = { timeoutMs?: number; raw?: boolean };

export class ApiClient {
  static setToken(token: string | null) {
    accessToken = token;
  }
  static getToken(): string | null {
    return accessToken;
  }

  static async initAuth(): Promise<boolean> {
    if (accessToken) return true;
    return !!(await performSilentRefresh());
  }

  private static async request<T = any>(endpoint: string, options: RequestInit = {}, opts: ReqOpts = {}): Promise<T> {
    const timeoutMs = opts.timeoutMs ?? 30000;
    const headers = new Headers(options.headers);
    if (!headers.has("Content-Type") && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
    if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);

    const send = () => fetchWithTimeout(urlFor(endpoint), { ...options, headers, credentials: "include" }, timeoutMs);
    let response = await send();

    if (response.status === 401 && endpoint !== "/api/auth/refresh" && endpoint !== "/api/auth/login") {
      const newToken = await performSilentRefresh();
      if (newToken) {
        headers.set("Authorization", `Bearer ${newToken}`);
        response = await send();
      }
    }
    if (!response.ok) throw await toApiError(response);
    if (opts.raw) return response as unknown as T;
    if (response.headers.get("content-type")?.includes("application/json")) return response.json();
    return response.blob() as unknown as T;
  }

  static guestLogin() {
    return this.request("/api/auth/guest", { method: "POST" });
  }

  static login(username: string, password: string, staySignedIn: boolean = true) {
    const formData = new FormData();
    formData.append("username", username.trim().toLowerCase());
    formData.append("password", password);
    return this.request(`/api/auth/login?remember_me=${staySignedIn}`, { method: "POST", body: formData });
  }

  static register(email: string, password: string, full_name?: string) {
    return this.request("/api/auth/register", { method: "POST", body: JSON.stringify({ email: email.trim().toLowerCase(), password, full_name }) });
  }
  static verifyEmail(token: string) {
    return this.request(`/api/auth/verify-email?token=${encodeURIComponent(token)}`, { method: "GET" });
  }
  static resendVerification(email: string) {
    return this.request("/api/auth/resend-verification", { method: "POST", body: JSON.stringify({ email: email.trim().toLowerCase() }) });
  }
  static convertGuest(email: string, password: string, full_name?: string) {
    return this.request("/api/auth/convert-guest", { method: "POST", body: JSON.stringify({ email: email.trim().toLowerCase(), password, full_name }) });
  }
  static googleLogin(idToken: string) {
    return this.request("/api/auth/google", { method: "POST", body: JSON.stringify({ id_token: idToken }) });
  }
  static forgotPassword(email: string) {
    return this.request("/api/auth/forgot-password", { method: "POST", body: JSON.stringify({ email: email.trim().toLowerCase() }) });
  }
  static resetPassword(token: string, new_password: string) {
    return this.request("/api/auth/reset-password", { method: "POST", body: JSON.stringify({ token, new_password }) });
  }

  /** The pipeline can legitimately take 1-2 minutes on a cold backend, so the timeout is generous. */
  static submitExtraction(message: string, target_url: string = "", session_id?: string) {
    return this.request("/api/chat/", { method: "POST", body: JSON.stringify({ message, target_url, session_id }) }, { timeoutMs: 170000 });
  }
  static getHistory(sessionId: string) {
    return this.request(`/api/chat/${sessionId}/history`, { method: "GET" });
  }
  static uploadFile(file: File, sessionId: string) {
    const formData = new FormData();
    formData.append("file", file);
    return this.request(`/api/upload/?session_id=${encodeURIComponent(sessionId)}`, { method: "POST", body: formData }, { timeoutMs: 120000 });
  }
  static getSessionData(sessionId: string, limit?: number) {
    return this.request(`/api/chat/${sessionId}/data${limit ? `?limit=${limit}` : ""}`, { method: "GET" });
  }
  static getSessions() {
    return this.request("/api/chat/sessions", { method: "GET" });
  }
  static renameSession(sessionId: string, title: string) {
    return this.request(`/api/chat/${encodeURIComponent(sessionId)}/rename`, {
      method: "PATCH",
      body: JSON.stringify({ title: title.trim() }),
    });
  }
  static deleteSession(sessionId: string) {
    return this.request(`/api/chat/${sessionId}`, { method: "DELETE" });
  }
  static getProgress(sessionId: string) {
    return this.request(`/api/chat/${sessionId}/progress`, { method: "GET" }, { timeoutMs: 8000 });
  }
  static getMe() {
    return this.request("/api/auth/me", { method: "GET" });
  }
  static updateMe(data: { full_name?: string | null }) {
    return this.request("/api/auth/me", { method: "PATCH", body: JSON.stringify(data) });
  }

  /** Download a server-generated export (csv | excel | json | markdown) with the correct filename + extension. */
  static async downloadExport(sessionId: string, format: "csv" | "excel" | "json" | "markdown"): Promise<void> {
    const response = await this.request<Response>(`/api/export/${format}?session_id=${encodeURIComponent(sessionId)}`, { method: "GET" }, { raw: true, timeoutMs: 60000 });
    const blob = await response.blob();
    const ext = { csv: "csv", excel: "xlsx", json: "json", markdown: "md" }[format];
    const match = /filename="?([^";]+)"?/i.exec(response.headers.get("content-disposition") || "");
    const filename = match?.[1] || `webiscrap_export.${ext}`;
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    playInterfaceSound("download");
    setTimeout(() => window.URL.revokeObjectURL(url), 2000);
  }

  static async logout() {
    try {
      await this.request("/api/auth/logout", { method: "POST", body: JSON.stringify({}) }, { timeoutMs: 8000 });
    } catch {
      // best-effort — the cookie must still be cleared client-side
    }
    accessToken = null;
    // Mark an explicit logout so the login page suppresses any Google OAuth auto-redirect result
    // that would otherwise silently re-authenticate the user immediately (the loop bug).
    try { localStorage.setItem("webiscrap_just_logged_out", "1"); } catch { /* ignore */ }
  }
}
