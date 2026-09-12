const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// In-memory access token storage (immune to localStorage XSS attacks)
let accessToken: string | null = null;

// Single-flight refresh lock (Section 12 / Refresh Race Condition)
// Concurrently arriving 401s share a single refresh request rather than rotating/revoking out from under each other
let refreshPromise: Promise<string | null> | null = null;

async function performSilentRefresh(): Promise<string | null> {
  if (refreshPromise) {
    return refreshPromise;
  }
  refreshPromise = (async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
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
      // Refresh failed — user is not authenticated or session invalid
    }
    return null;
  })().finally(() => {
    refreshPromise = null;
  });

  return refreshPromise;
}

export class ApiClient {
  /** Set the in-memory access token (called after login/refresh). */
  static setToken(token: string | null) {
    accessToken = token;
  }

  /** Read the current in-memory access token (for auth guards). */
  static getToken(): string | null {
    return accessToken;
  }

  /**
   * Bootstrap auth on page load by attempting a single silent refresh.
   * Returns true if auth was restored, false otherwise.
   */
  static async initAuth(): Promise<boolean> {
    if (accessToken) return true;
    const token = await performSilentRefresh();
    return !!token;
  }

  private static async request(endpoint: string, options: RequestInit = {}) {
    const token = accessToken;
    
    const headers = new Headers(options.headers);
    // Only set Content-Type for non-FormData bodies
    if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
      headers.set("Content-Type", "application/json");
    }
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    let response: Response;
    try {
      response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
        credentials: "include",
      });
    } catch {
      throw new Error("Network error. Make sure the backend server is running.");
    }

    if (!response.ok) {
      // Handle 401 using single-flight refresh mechanism
      if (response.status === 401 && endpoint !== "/api/auth/refresh") {
        const newToken = await performSilentRefresh();
        if (newToken) {
          headers.set("Authorization", `Bearer ${newToken}`);
          response = await fetch(`${API_BASE_URL}${endpoint}`, { 
            ...options, 
            headers,
            credentials: "include"
          });
          if (response.ok) {
            if (response.headers.get("content-type")?.includes("application/json")) return response.json();
            return response.blob();
          }
        }
      }
      
      const errorData = await response.json().catch(() => ({}));
      const err = new Error(errorData.detail || `API Error: ${response.statusText}`) as any;
      err.status = response.status;
      err.detail = errorData.detail;
      throw err;
    }

    if (response.headers.get("content-type")?.includes("application/json")) {
      return response.json();
    }
    return response.blob();
  }

  static async guestLogin() {
    return this.request("/api/auth/guest", { method: "POST" });
  }

  static async login(username: string, password: string, staySignedIn: boolean = true) {
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);
    
    // Do NOT set Content-Type header -- browser sets multipart boundary
    return this.request(`/api/auth/login?remember_me=${staySignedIn}`, { 
      method: "POST",
      body: formData,
    });
  }

  static async register(email: string, password: string, full_name?: string) {
    return this.request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name }),
    });
  }

  static async verifyEmail(token: string) {
    return this.request(`/api/auth/verify-email?token=${encodeURIComponent(token)}`, {
      method: "GET",
    });
  }

  static async resendVerification(email: string) {
    return this.request("/api/auth/resend-verification", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
  }

  static async convertGuest(email: string, password: string, full_name?: string) {
    return this.request("/api/auth/convert-guest", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name }),
    });
  }

  static async googleLogin(idToken: string) {
    return this.request("/api/auth/google", {
      method: "POST",
      body: JSON.stringify({ id_token: idToken }),
    });
  }

  static async phoneLogin(idToken: string) {
    return this.request("/api/auth/phone", {
      method: "POST",
      body: JSON.stringify({ id_token: idToken }),
    });
  }

  static async forgotPassword(email: string) {
    return this.request("/api/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
  }

  static async resetPassword(token: string, new_password: string) {
    return this.request("/api/auth/reset-password", {
      method: "POST",
      body: JSON.stringify({ token, new_password }),
    });
  }

  static async submitExtraction(message: string, target_url: string = "", session_id?: string) {
    return this.request("/api/chat/", {
      method: "POST",
      body: JSON.stringify({ message, target_url, session_id })
    });
  }

  static async getHistory(sessionId: string) {
    return this.request(`/api/chat/${sessionId}/history`, { method: "GET" });
  }

  static async uploadFile(file: File, sessionId?: string) {
    const formData = new FormData();
    formData.append("file", file);
    const query = sessionId ? `?session_id=${sessionId}` : "";
    return this.request(`/api/upload/${query}`, {
      method: "POST",
      body: formData,
    });
  }

  static async getSessionData(sessionId: string) {
    return this.request(`/api/chat/${sessionId}/data`, { method: "GET" });
  }

  static async getSessions() {
    return this.request("/api/chat/sessions", { method: "GET" });
  }

  static async getProgress(sessionId: string) {
    return this.request(`/api/chat/${sessionId}/progress`, { method: "GET" });
  }

  static async getMe() {
    return this.request("/api/auth/me", { method: "GET" });
  }

  static async logout() {
    try {
      await this.request("/api/auth/logout", {
        method: "POST",
        body: JSON.stringify({}),
      });
    } catch {
      // Best-effort logout
    }
    accessToken = null;
  }
}
