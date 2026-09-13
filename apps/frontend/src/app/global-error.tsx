"use client";

import { useEffect } from "react";

interface GlobalErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: GlobalErrorProps) {
  useEffect(() => {
    // Log error for debugging — never expose to the user
    console.error("[GlobalError boundary]", error);
  }, [error]);

  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#05070c",
          fontFamily: "system-ui, -apple-system, sans-serif",
          color: "#e8eaf0",
          padding: "24px",
          boxSizing: "border-box",
        }}
      >
        <div
          style={{
            maxWidth: 420,
            width: "100%",
            textAlign: "center",
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 16,
            padding: "40px 32px",
            background: "rgba(255,255,255,0.03)",
          }}
        >
          <p
            style={{
              fontFamily: "monospace",
              fontSize: 11,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              color: "#1477f5",
              marginBottom: 16,
            }}
          >
            Critical error
          </p>

          <h1
            style={{
              fontSize: 22,
              fontWeight: 600,
              margin: "0 0 12px",
              color: "#e8eaf0",
            }}
          >
            Application failed to load.
          </h1>

          <p
            style={{
              fontSize: 14,
              color: "#8a8fa8",
              lineHeight: 1.6,
              margin: "0 0 28px",
            }}
          >
            A critical error prevented the page from rendering. Please try
            again — if the problem persists, refresh your browser.
          </p>

          <button
            id="global-error-retry-btn"
            onClick={reset}
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              padding: "10px 24px",
              borderRadius: 9999,
              border: "1px solid rgba(130,190,255,0.4)",
              background: "linear-gradient(180deg, #1477f5 0%, #0f5cc8 100%)",
              color: "#ffffff",
              fontSize: 14,
              fontWeight: 500,
              cursor: "pointer",
              transition: "filter 0.15s",
            }}
            onMouseEnter={(e) =>
              ((e.currentTarget as HTMLButtonElement).style.filter =
                "brightness(1.1)")
            }
            onMouseLeave={(e) =>
              ((e.currentTarget as HTMLButtonElement).style.filter = "")
            }
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
