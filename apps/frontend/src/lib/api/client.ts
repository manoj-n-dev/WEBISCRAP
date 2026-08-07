const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiClient {
  private static async request(endpoint: string, options: RequestInit = {}) {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    
    const headers = new Headers(options.headers);
    if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
      headers.set("Content-Type", "application/json");
    }
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
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
    
    return this.request("/api/auth/login", { 
      method: "POST",
      body: formData,
      headers: {
        // Fetch will automatically set the correct Content-Type for FormData,
        // but we need to delete it from the defaults so it boundary is set correctly
      }
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
