const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiClient {
  private static async request(endpoint: string, options: RequestInit = {}) {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    
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
      });
    } catch {
      throw new Error("Network error. Make sure the backend server is running.");
    }

    if (!response.ok) {
      if (response.status === 401 && endpoint !== "/api/auth/refresh") {
        const refreshToken = typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;
        if (refreshToken) {
          try {
            const refreshRes = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ refresh_token: refreshToken })
            });
            if (refreshRes.ok) {
              const data = await refreshRes.json();
              localStorage.setItem("token", data.access_token);
              localStorage.setItem("refresh_token", data.refresh_token);
              // Retry the original request
              headers.set("Authorization", `Bearer ${data.access_token}`);
              response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
              if (response.ok) {
                if (response.headers.get("content-type")?.includes("application/json")) return response.json();
                return response.blob();
              }
            }
          } catch (e) {
            // Refresh failed, fall through to error handling
          }
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

  static async login(username: string, password: string) {
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);
    
    // Do NOT set Content-Type header -- browser must set it with the multipart boundary
    return this.request("/api/auth/login", { 
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
}
