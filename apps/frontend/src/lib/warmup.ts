/** Wakes the (free-tier, sleeping) backend. Runs at most once every 4 minutes per browser tab. */
export function warmUpBackend() {
  if (typeof window === "undefined") return;
  try {
    const last = Number(window.sessionStorage.getItem("ws_warm") || 0);
    if (Date.now() - last < 4 * 60 * 1000) return;
    window.sessionStorage.setItem("ws_warm", String(Date.now()));
  } catch {
    /* storage may be blocked; still fire once */
  }
  const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
  const base = process.env.NEXT_PUBLIC_API_URL || (isLocal ? "http://localhost:8000" : "https://webiscrap-api.onrender.com");
  fetch(`${base}/health`, { mode: "no-cors", cache: "no-store", keepalive: true }).catch(() => {});
}
