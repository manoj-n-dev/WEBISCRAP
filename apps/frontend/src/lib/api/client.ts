const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// FIX 7 (H3): Access token stored in-memory instead of localStorage.
// This prevents XSS from reading the token. The refresh token is already
// stored as an httpOnly cookie and is never accessible to JS.
let accessToken: string | null = null;

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
   * Bootstrap auth on page load by attempting a silent refresh.
   * Returns true if auth was restored, false otherwise.
   */
  static async initAuth(): Promise<boolean> {
    if (accessToken) return true;
    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({}),
      });
      if (res.ok) {
        const data = await res.json();
        accessToken = data.access_token;
        return true;
      }
    } catch {
      // Refresh failed — user is not authenticated
    }
    return false;
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
      if (response.status === 401 && endpoint !== "/api/auth/refresh") {
        try {
          const refreshRes = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({}) // Backend will read from cookie
          });
          if (refreshRes.ok) {
            const data = await refreshRes.json();
            accessToken = data.access_token;
            // Retry the original request
            headers.set("Authorization", `Bearer ${data.access_token}`);
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
        } catch (e) {
          // Refresh failed, fall through to error handling
        }
      }
      
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API Error: ${response.statusText}`);
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
    
    // Do NOT set Content-Type header -- browser must set it with the multipart boundary
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

  static async submitExtraction(message: string, target_url: string = "", session_id?: string) {
    return this.request("/api/chat/", {
      method: "POST",
      body: JSON.stringify({ message, target_url, session_id })
    });
  }

  static async getHistory(sessionId: string) {
    return this.request(`/api/chat/${sessionId}/history`, { method: "GET" });
  }

  // H4: File upload
  static async uploadFile(file: File, sessionId?: string) {
    const formData = new FormData();
    formData.append("file", file);
    const query = sessionId ? `?session_id=${sessionId}` : "";
    return this.request(`/api/upload/${query}`, {
      method: "POST",
      body: formData,
    });
  }

  // H6: Fetch session data for dataset view
  static async getSessionData(sessionId: string) {
    return this.request(`/api/chat/${sessionId}/data`, { method: "GET" });
  }

  // H9: Fetch session list for sidebar
  static async getSessions() {
    return this.request("/api/chat/sessions", { method: "GET" });
  }

  // M9: Fetch pipeline progress
  static async getProgress(sessionId: string) {
    return this.request(`/api/chat/${sessionId}/progress`, { method: "GET" });
  }

  // FIX 11 (M2): Fetch current user info
  static async getMe() {
    return this.request("/api/auth/me", { method: "GET" });
  }

  // M5: Logout
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

