import type { NextConfig } from "next";

const BACKEND = (process.env.NEXT_PUBLIC_API_URL || "https://webiscrap-api.onrender.com").replace(/\/$/, "");

const nextConfig: NextConfig = {
  async headers() {
    // Non-fingerprinted static images (logo, icons, manifest): let browsers/CDN reuse them for a day. (/_next/static is already immutable.)
    return [
      { source: "/:all*(png|ico|webp|svg|jpg|jpeg)", headers: [{ key: "Cache-Control", value: "public, max-age=86400, stale-while-revalidate=604800" }] },
      { source: "/manifest.webmanifest", headers: [{ key: "Cache-Control", value: "public, max-age=86400" }] },
    ];
  },
  async rewrites() {
    // Same-origin proxy for the cookie-bearing auth endpoints (login / guest / refresh / logout / google ...).
    // The refresh cookie is then set for the site's own domain (first-party) and survives Safari/iOS, Brave and
    // Chrome-incognito third-party-cookie blocking. Disable with NEXT_PUBLIC_AUTH_PROXY=false.
    if (process.env.NEXT_PUBLIC_AUTH_PROXY === "false") return [];
    return [{ source: "/api/auth/:path*", destination: `${BACKEND}/api/auth/:path*` }];
  },
};

export default nextConfig;
