"use client";

import { useEffect } from "react";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function AppError({ error, reset }: ErrorProps) {
  useEffect(() => {
    // Log error for debugging — never expose to the user
    console.error("[AppError boundary]", error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-0 px-6">
      {/* Subtle warning-tinted radial glow */}
      <div
        className="pointer-events-none fixed inset-0"
        aria-hidden="true"
        style={{
          background:
            "radial-gradient(ellipse 60% 40% at 50% 20%, rgba(245,80,80,0.06) 0%, transparent 70%)",
        }}
      />

      <Card className="relative z-10 w-full max-w-md text-center rounded-2xl p-1">
        <CardHeader className="pb-2">
          {/* Status badge */}
          <span className="inline-block mx-auto mb-4 px-3 py-1 rounded-full border border-glass-border-strong bg-white/5 font-mono text-[11px] text-signal-400 uppercase tracking-[0.08em]">
            Unexpected error
          </span>

          <CardTitle className="text-[26px] font-display font-semibold text-text-hi">
            Something went wrong.
          </CardTitle>
        </CardHeader>

        <CardContent className="flex flex-col items-center gap-6">
          <CardDescription className="text-[14px] text-text-dim leading-relaxed max-w-[300px]">
            An unexpected error occurred in this view. You can try again or
            start a new extraction from scratch.
          </CardDescription>

          <div className="flex flex-col sm:flex-row gap-3 w-full justify-center">
            <Button variant="primary" onClick={reset} id="error-retry-btn">
              Try again
            </Button>
            <Button variant="ghost" asChild>
              <Link href="/">Start new extraction</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
